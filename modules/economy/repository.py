from decimal import Decimal
from datetime import datetime

from .config import STARTING_BALANCE
from .database import db
from .utils import money_decimal, now


# ============================================================
# ACCOUNTS
# ============================================================

async def ensure_account(
    guild_id: int,
    user_id: int,
):
    current = now()

    result = await db.fetchone(
        """
        INSERT INTO accounts (
            guild_id,
            user_id,
            balance,
            created_at,
            updated_at
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (guild_id, user_id)
        DO NOTHING
        RETURNING balance
        """,
        (
            guild_id,
            user_id,
            STARTING_BALANCE,
            current,
            current,
        ),
    )

    if result:
        if STARTING_BALANCE > 0:
            await db.execute(
                """
                INSERT INTO transactions (
                    guild_id,
                    from_user_id,
                    to_user_id,
                    amount,
                    type,
                    description,
                    timestamp
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    guild_id,
                    None,
                    user_id,
                    STARTING_BALANCE,
                    "initial",
                    "Saldo inicial",
                    current,
                ),
            )

        return Decimal(str(result[0]))

    result = await db.fetchone(
        """
        SELECT balance
        FROM accounts
        WHERE guild_id = %s
        AND user_id = %s
        """,
        (
            guild_id,
            user_id,
        ),
    )

    if not result:
        return Decimal("0")

    return Decimal(str(result[0]))


async def get_balance(
    guild_id: int,
    user_id: int,
):
    await ensure_account(
        guild_id,
        user_id,
    )

    result = await db.fetchone(
        """
        SELECT balance
        FROM accounts
        WHERE guild_id = %s
        AND user_id = %s
        """,
        (
            guild_id,
            user_id,
        ),
    )

    if not result:
        return Decimal("0")

    return Decimal(str(result[0]))


# ============================================================
# MONEY
# ============================================================

async def add_money(
    guild_id: int,
    user_id: int,
    amount,
    transaction_type="reward",
    description=None,
):
    amount = money_decimal(amount)

    if amount <= 0:
        return False

    await ensure_account(
        guild_id,
        user_id,
    )

    current = now()

    if db.pool is None:
        raise RuntimeError("Database no conectada")

    async with db.pool.connection() as conn:
        async with conn.transaction():
            async with conn.cursor() as cursor:

                await cursor.execute(
                    """
                    UPDATE accounts
                    SET
                        balance = balance + %s,
                        updated_at = %s
                    WHERE guild_id = %s
                    AND user_id = %s
                    """,
                    (
                        amount,
                        current,
                        guild_id,
                        user_id,
                    ),
                )

                await cursor.execute(
                    """
                    INSERT INTO transactions (
                        guild_id,
                        from_user_id,
                        to_user_id,
                        amount,
                        type,
                        description,
                        timestamp
                    )
                    VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s
                    )
                    """,
                    (
                        guild_id,
                        None,
                        user_id,
                        amount,
                        transaction_type,
                        description,
                        current,
                    ),
                )

    return True


async def remove_money(
    guild_id: int,
    user_id: int,
    amount,
    transaction_type="remove",
    description=None,
):
    amount = money_decimal(amount)

    if amount <= 0:
        return False

    await ensure_account(
        guild_id,
        user_id,
    )

    current = now()

    if db.pool is None:
        raise RuntimeError("Database no conectada")

    async with db.pool.connection() as conn:
        async with conn.transaction():
            async with conn.cursor() as cursor:

                await cursor.execute(
                    """
                    UPDATE accounts
                    SET
                        balance = balance - %s,
                        updated_at = %s
                    WHERE guild_id = %s
                    AND user_id = %s
                    AND balance >= %s
                    RETURNING balance
                    """,
                    (
                        amount,
                        current,
                        guild_id,
                        user_id,
                        amount,
                    ),
                )

                result = await cursor.fetchone()

                if not result:
                    return False

                await cursor.execute(
                    """
                    INSERT INTO transactions (
                        guild_id,
                        from_user_id,
                        to_user_id,
                        amount,
                        type,
                        description,
                        timestamp
                    )
                    VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s
                    )
                    """,
                    (
                        guild_id,
                        user_id,
                        None,
                        amount,
                        transaction_type,
                        description,
                        current,
                    ),
                )

    return True


async def transfer_money(
    guild_id: int,
    from_user_id: int,
    to_user_id: int,
    amount,
):
    amount = money_decimal(amount)

    if amount <= 0:
        return False, "La cantidad debe ser mayor que 0."

    if from_user_id == to_user_id:
        return False, "No puedes enviarte monedas a ti mismo."

    await ensure_account(
        guild_id,
        from_user_id,
    )

    await ensure_account(
        guild_id,
        to_user_id,
    )

    current = now()

    if db.pool is None:
        raise RuntimeError("Database no conectada")

    async with db.pool.connection() as conn:
        async with conn.transaction():
            async with conn.cursor() as cursor:

                await cursor.execute(
                    """
                    UPDATE accounts
                    SET
                        balance = balance - %s,
                        updated_at = %s
                    WHERE guild_id = %s
                    AND user_id = %s
                    AND balance >= %s
                    RETURNING balance
                    """,
                    (
                        amount,
                        current,
                        guild_id,
                        from_user_id,
                        amount,
                    ),
                )

                sender = await cursor.fetchone()

                if not sender:
                    return (
                        False,
                        "No tienes suficientes monedas.",
                    )

                await cursor.execute(
                    """
                    UPDATE accounts
                    SET
                        balance = balance + %s,
                        updated_at = %s
                    WHERE guild_id = %s
                    AND user_id = %s
                    """,
                    (
                        amount,
                        current,
                        guild_id,
                        to_user_id,
                    ),
                )

                await cursor.execute(
                    """
                    INSERT INTO transactions (
                        guild_id,
                        from_user_id,
                        to_user_id,
                        amount,
                        type,
                        description,
                        timestamp
                    )
                    VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s
                    )
                    """,
                    (
                        guild_id,
                        from_user_id,
                        to_user_id,
                        amount,
                        "transfer",
                        "Transferencia entre usuarios",
                        current,
                    ),
                )

    return True, None


# ============================================================
# VOICE
# ============================================================

async def ensure_voice_activity(
    guild_id: int,
    user_id: int,
):
    await db.execute(
        """
        INSERT INTO voice_activity (
            guild_id,
            user_id,
            total_seconds,
            total_earned,
            updated_at
        )
        VALUES (%s, %s, 0, 0, %s)
        ON CONFLICT (guild_id, user_id)
        DO NOTHING
        """,
        (
            guild_id,
            user_id,
            now(),
        ),
    )


async def get_voice_stats(
    guild_id: int,
    user_id: int,
):
    return await db.fetchone(
        """
        SELECT
            total_seconds,
            total_earned
        FROM voice_activity
        WHERE guild_id = %s
        AND user_id = %s
        """,
        (
            guild_id,
            user_id,
        ),
    )


async def get_voice_session(
    guild_id: int,
    user_id: int,
):
    return await db.fetchone(
        """
        SELECT
            joined_at,
            last_paid_at
        FROM economy_voice_sessions
        WHERE guild_id = %s
        AND user_id = %s
        """,
        (
            guild_id,
            user_id,
        ),
    )


async def get_active_voice_sessions(
    guild_id: int,
):
    return await db.fetchall(
        """
        SELECT
            user_id,
            last_paid_at
        FROM economy_voice_sessions
        WHERE guild_id = %s
        """,
        (guild_id,),
    )


async def start_voice_session(
    guild_id: int,
    user_id: int,
):
    await ensure_account(
        guild_id,
        user_id,
    )

    await ensure_voice_activity(
        guild_id,
        user_id,
    )

    current = now()

    result = await db.fetchone(
        """
        INSERT INTO economy_voice_sessions (
            guild_id,
            user_id,
            joined_at,
            last_paid_at
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (guild_id, user_id)
        DO NOTHING
        RETURNING user_id
        """,
        (
            guild_id,
            user_id,
            current,
            current,
        ),
    )

    return result is not None


async def update_voice_session(
    guild_id: int,
    user_id: int,
    last_paid_at: datetime,
):
    await db.execute(
        """
        UPDATE economy_voice_sessions
        SET last_paid_at = %s
        WHERE guild_id = %s
        AND user_id = %s
        """,
        (
            last_paid_at,
            guild_id,
            user_id,
        ),
    )


async def delete_voice_session(
    guild_id: int,
    user_id: int,
):
    await db.execute(
        """
        DELETE FROM economy_voice_sessions
        WHERE guild_id = %s
        AND user_id = %s
        """,
        (
            guild_id,
            user_id,
        ),
    )


async def add_voice_time(
    guild_id: int,
    user_id: int,
    seconds: int,
    reward,
):
    minutes = seconds // 60

    if minutes <= 0:
        return False

    seconds_to_process = minutes * 60
    current = now()

    await ensure_voice_activity(
        guild_id,
        user_id,
    )

    await ensure_account(
        guild_id,
        user_id,
    )

    if db.pool is None:
        raise RuntimeError("Database no conectada")

    async with db.pool.connection() as conn:
        async with conn.transaction():
            async with conn.cursor() as cursor:

                await cursor.execute(
                    """
                    UPDATE voice_activity
                    SET
                        total_seconds =
                            total_seconds + %s,
                        total_earned =
                            total_earned + %s,
                        updated_at = %s
                    WHERE guild_id = %s
                    AND user_id = %s
                    """,
                    (
                        seconds_to_process,
                        reward,
                        current,
                        guild_id,
                        user_id,
                    ),
                )

                await cursor.execute(
                    """
                    UPDATE accounts
                    SET
                        balance = balance + %s,
                        updated_at = %s
                    WHERE guild_id = %s
                    AND user_id = %s
                    """,
                    (
                        reward,
                        current,
                        guild_id,
                        user_id,
                    ),
                )

                await cursor.execute(
                    """
                    INSERT INTO transactions (
                        guild_id,
                        from_user_id,
                        to_user_id,
                        amount,
                        type,
                        description,
                        timestamp
                    )
                    VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s
                    )
                    """,
                    (
                        guild_id,
                        None,
                        user_id,
                        reward,
                        "voice_activity",
                        f"Actividad en voz: {minutes} minuto(s)",
                        current,
                    ),
                )

    return True


async def get_leaderboard(
    guild_id: int,
    limit: int = 10,
):
    return await db.fetchall(
        """
        SELECT
            user_id,
            balance
        FROM accounts
        WHERE guild_id = %s
        ORDER BY balance DESC
        LIMIT %s
        """,
        (
            guild_id,
            limit,
        ),
    )