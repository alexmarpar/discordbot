from .database import db


TABLES = """
CREATE TABLE IF NOT EXISTS accounts (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    balance NUMERIC(20, 2)
        NOT NULL
        DEFAULT 0,

    created_at TIMESTAMPTZ
        NOT NULL,

    updated_at TIMESTAMPTZ
        NOT NULL,

    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,

    guild_id BIGINT NOT NULL,

    from_user_id BIGINT,
    to_user_id BIGINT,

    amount NUMERIC(20, 2)
        NOT NULL,

    type TEXT NOT NULL,

    description TEXT,

    timestamp TIMESTAMPTZ
        NOT NULL
);


CREATE TABLE IF NOT EXISTS voice_activity (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    total_seconds BIGINT
        NOT NULL
        DEFAULT 0,

    total_earned NUMERIC(20, 2)
        NOT NULL
        DEFAULT 0,

    updated_at TIMESTAMPTZ
        NOT NULL,

    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE IF NOT EXISTS economy_voice_sessions (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    joined_at TIMESTAMPTZ
        NOT NULL,

    last_paid_at TIMESTAMPTZ
        NOT NULL,

    PRIMARY KEY (guild_id, user_id)
);
"""


INDEXES = """
CREATE INDEX IF NOT EXISTS
idx_accounts_guild_balance
ON accounts(guild_id, balance DESC);


CREATE INDEX IF NOT EXISTS
idx_transactions_guild
ON transactions(guild_id);


CREATE INDEX IF NOT EXISTS
idx_transactions_users
ON transactions(
    guild_id,
    from_user_id,
    to_user_id
);


CREATE INDEX IF NOT EXISTS
idx_voice_activity_guild
ON voice_activity(
    guild_id,
    total_seconds DESC
);


CREATE INDEX IF NOT EXISTS
idx_economy_voice_sessions_guild
ON economy_voice_sessions(guild_id);
"""


EXPECTED_TABLES = {
    "accounts",
    "transactions",
    "voice_activity",
    "economy_voice_sessions",
}


async def init_schema():
    print(
        "[ECONOMY][DB] Checking schema...",
        flush=True,
    )

    for statement in TABLES.split(";"):
        statement = statement.strip()

        if statement:
            await db.execute(statement)

    for statement in INDEXES.split(";"):
        statement = statement.strip()

        if statement:
            await db.execute(statement)

    tables = await db.fetchall("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)

    table_names = {
        row[0]
        for row in tables
    }

    missing = EXPECTED_TABLES - table_names

    if missing:
        print(
            "[ECONOMY][DB] "
            f"⚠️ Missing tables: {sorted(missing)}",
            flush=True,
        )
    else:
        print(
            "[ECONOMY][DB] "
            "✅ All tables exist",
            flush=True,
        )

    print(
        "[ECONOMY][DB] Schema ready",
        flush=True,
    )