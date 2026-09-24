from datetime import datetime

import discord

from .database import db
from .utils import now


# ============================================================
# USERS
# ============================================================

async def ensure_user(member: discord.Member):
    guild_id = member.guild.id
    user_id = member.id

    await db.execute(
        """
        INSERT INTO users (
            guild_id,
            user_id,
            username,
            display_name,
            created_at,
            joined_at,
            first_seen,
            last_seen
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)

        ON CONFLICT (guild_id, user_id)
        DO UPDATE SET
            username = EXCLUDED.username,
            display_name = EXCLUDED.display_name,
            last_seen = EXCLUDED.last_seen
        """,
        (
            guild_id,
            user_id,
            str(member),
            member.display_name,
            member.created_at,
            member.joined_at,
            now(),
            now(),
        ),
    )


async def update_last_seen(
    guild_id: int,
    user_id: int,
    text_channel_id: int | None = None,
    voice_channel_id: int | None = None,
):
    if text_channel_id is not None:
        await db.execute(
            """
            UPDATE users
            SET
                last_seen = %s,
                last_text_channel_id = %s
            WHERE guild_id = %s
              AND user_id = %s
            """,
            (
                now(),
                text_channel_id,
                guild_id,
                user_id,
            ),
        )

    elif voice_channel_id is not None:
        await db.execute(
            """
            UPDATE users
            SET
                last_seen = %s,
                last_voice_channel_id = %s
            WHERE guild_id = %s
              AND user_id = %s
            """,
            (
                now(),
                voice_channel_id,
                guild_id,
                user_id,
            ),
        )

    else:
        await db.execute(
            """
            UPDATE users
            SET last_seen = %s
            WHERE guild_id = %s
              AND user_id = %s
            """,
            (
                now(),
                guild_id,
                user_id,
            ),
        )


# ============================================================
# MESSAGES
# ============================================================

async def add_message(
    guild_id: int,
    user_id: int,
    channel_id: int,
    timestamp,
    characters: int,
    attachments: int,
    links: int,
):
    await db.execute(
        """
        INSERT INTO messages (
            guild_id,
            user_id,
            channel_id,
            timestamp,
            characters,
            attachments,
            links
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            guild_id,
            user_id,
            channel_id,
            timestamp,
            characters,
            attachments,
            links,
        ),
    )

    await db.execute(
        """
        UPDATE users
        SET
            messages = messages + 1,
            characters = characters + %s,
            attachments = attachments + %s,
            links = links + %s,
            last_seen = %s,
            last_text_channel_id = %s
        WHERE guild_id = %s
          AND user_id = %s
        """,
        (
            characters,
            attachments,
            links,
            timestamp,
            channel_id,
            guild_id,
            user_id,
        ),
    )

async def add_message_edit(
    guild_id: int,
    user_id: int,
    channel_id: int | None,
    message_id: int | None,
):
    timestamp = now()

    await db.execute(
        """
        INSERT INTO message_edits (
            guild_id,
            user_id,
            channel_id,
            message_id,
            timestamp
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            guild_id,
            user_id,
            channel_id,
            message_id,
            timestamp,
        ),
    )

    await db.execute(
        """
        UPDATE users
        SET
            messages_edited = messages_edited + 1,
            last_seen = %s
        WHERE guild_id = %s
          AND user_id = %s
        """,
        (
            timestamp,
            guild_id,
            user_id,
        ),
    )


async def add_message_deletion(
    guild_id: int,
    user_id: int | None,
    channel_id: int | None,
    message_id: int | None,
):
    timestamp = now()

    await db.execute(
        """
        INSERT INTO message_deletions (
            guild_id,
            user_id,
            channel_id,
            message_id,
            timestamp
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            guild_id,
            user_id,
            channel_id,
            message_id,
            timestamp,
        ),
    )

    if user_id is not None:
        await db.execute(
            """
            UPDATE users
            SET
                messages_deleted = messages_deleted + 1,
                last_seen = %s
            WHERE guild_id = %s
              AND user_id = %s
            """,
            (
                timestamp,
                guild_id,
                user_id,
            ),
        )


# ============================================================
# REACTIONS
# ============================================================

async def add_reaction(
    guild_id: int,
    user_id: int,
    channel_id: int | None,
    message_id: int | None,
    emoji: str | None,
):
    timestamp = now()

    await db.execute(
        """
        INSERT INTO reactions (
            guild_id,
            user_id,
            channel_id,
            message_id,
            emoji,
            timestamp
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            guild_id,
            user_id,
            channel_id,
            message_id,
            emoji,
            timestamp,
        ),
    )

    await db.execute(
        """
        UPDATE users
        SET
            reactions_added = reactions_added + 1,
            last_seen = %s
        WHERE guild_id = %s
          AND user_id = %s
        """,
        (
            timestamp,
            guild_id,
            user_id,
        ),
    )


# ============================================================
# TYPING
# ============================================================

async def add_typing_event(
    guild_id: int,
    user_id: int,
    channel_id: int | None = None,
):
    timestamp = now()

    await db.execute(
        """
        UPDATE users
        SET
            typing_events = typing_events + 1,
            last_seen = %s,
            last_text_channel_id = COALESCE(%s, last_text_channel_id)
        WHERE guild_id = %s
          AND user_id = %s
        """,
        (
            timestamp,
            channel_id,
            guild_id,
            user_id,
        ),
    )


# ============================================================
# MEMBER EVENTS
# ============================================================

async def add_member_event(
    guild_id: int,
    user_id: int,
    event: str,
):
    await db.execute(
        """
        INSERT INTO member_events (
            guild_id,
            user_id,
            event,
            timestamp
        )
        VALUES (%s, %s, %s, %s)
        """,
        (
            guild_id,
            user_id,
            event,
            now(),
        ),
    )


# ============================================================
# SERVER STATS
# ============================================================
async def get_server_stats(guild_id: int):
    # --------------------------------------------------------
    # Users
    # --------------------------------------------------------

    users_row = await db.fetchone(
        """
        SELECT
            COUNT(*) AS total_users,
            COALESCE(SUM(messages), 0) AS total_messages,
            COALESCE(SUM(characters), 0) AS total_characters
        FROM users
        WHERE guild_id = %s
        """,
        (guild_id,),
    )

    total_users = users_row[0] or 0
    total_messages = users_row[1] or 0
    total_characters = users_row[2] or 0

    # users no tiene columna is_bot.
    # Los bots se cuentan desde Discord en otro punto si se desea.
    bots = 0

    # --------------------------------------------------------
    # Active users
    # --------------------------------------------------------

    active_row = await db.fetchone(
        """
        SELECT COUNT(*)
        FROM users
        WHERE guild_id = %s
          AND last_seen >= NOW() - INTERVAL '7 days'
        """,
        (guild_id,),
    )

    active_users = active_row[0] or 0

    # --------------------------------------------------------
    # Weekly messages
    # --------------------------------------------------------

    weekly_row = await db.fetchone(
        """
        SELECT COUNT(*)
        FROM messages
        WHERE guild_id = %s
          AND timestamp >= NOW() - INTERVAL '7 days'
        """,
        (guild_id,),
    )

    weekly_messages = weekly_row[0] or 0

    # --------------------------------------------------------
    # Monthly messages
    # --------------------------------------------------------

    monthly_row = await db.fetchone(
        """
        SELECT COUNT(*)
        FROM messages
        WHERE guild_id = %s
          AND timestamp >= NOW() - INTERVAL '30 days'
        """,
        (guild_id,),
    )

    monthly_messages = monthly_row[0] or 0

    # --------------------------------------------------------
    # Voice
    # --------------------------------------------------------

    voice_row = await db.fetchone(
        """
        SELECT COALESCE(SUM(duration_seconds), 0)
        FROM voice_sessions
        WHERE guild_id = %s
        """,
        (guild_id,),
    )

    total_voice = voice_row[0] or 0

    # --------------------------------------------------------
    # Member joins / leaves
    # --------------------------------------------------------

    joins_row = await db.fetchone(
        """
        SELECT COUNT(*)
        FROM member_events
        WHERE guild_id = %s
          AND event = 'join'
        """,
        (guild_id,),
    )

    leaves_row = await db.fetchone(
        """
        SELECT COUNT(*)
        FROM member_events
        WHERE guild_id = %s
          AND event = 'leave'
        """,
        (guild_id,),
    )

    joins = joins_row[0] or 0
    leaves = leaves_row[0] or 0

    # --------------------------------------------------------
    # Busiest hour
    # --------------------------------------------------------

    busiest_hour_row = await db.fetchone(
        """
        SELECT
            EXTRACT(HOUR FROM timestamp)::INT AS hour,
            COUNT(*) AS total
        FROM messages
        WHERE guild_id = %s
        GROUP BY hour
        ORDER BY total DESC
        LIMIT 1
        """,
        (guild_id,),
    )

    if busiest_hour_row:
        busiest_hour = (
            busiest_hour_row[0],
            busiest_hour_row[1],
        )
    else:
        busiest_hour = None

    # --------------------------------------------------------
    # Busiest day
    # --------------------------------------------------------

    busiest_day_row = await db.fetchone(
        """
        SELECT
            EXTRACT(DOW FROM timestamp)::INT AS day,
            COUNT(*) AS total
        FROM messages
        WHERE guild_id = %s
        GROUP BY day
        ORDER BY total DESC
        LIMIT 1
        """,
        (guild_id,),
    )

    if busiest_day_row:
        busiest_day = (
            busiest_day_row[0],
            busiest_day_row[1],
        )
    else:
        busiest_day = None

    # --------------------------------------------------------
    # Top users
    # --------------------------------------------------------

    top_users = await db.fetchall(
        """
        SELECT
            user_id,
            display_name,
            messages,
            characters
        FROM users
        WHERE guild_id = %s
        ORDER BY messages DESC
        LIMIT 10
        """,
        (guild_id,),
    )

    # --------------------------------------------------------
    # Top voice users
    # --------------------------------------------------------

    top_voice = await db.fetchall(
        """
        SELECT
            user_id,
            display_name,
            voice_seconds
        FROM users
        WHERE guild_id = %s
        ORDER BY voice_seconds DESC
        LIMIT 10
        """,
        (guild_id,),
    )

    # --------------------------------------------------------
    # Top channels
    # --------------------------------------------------------

    top_channels = await db.fetchall(
        """
        SELECT
            channel_id,
            COUNT(*) AS total
        FROM messages
        WHERE guild_id = %s
        GROUP BY channel_id
        ORDER BY total DESC
        LIMIT 10
        """,
        (guild_id,),
    )

    return {
        "total_users": total_users,
        "bots": bots,
        "active_users": active_users,
        "total_messages": total_messages,
        "weekly_messages": weekly_messages,
        "monthly_messages": monthly_messages,
        "total_characters": total_characters,
        "total_voice": total_voice,
        "joins": joins,
        "leaves": leaves,
        "busiest_hour": busiest_hour,
        "busiest_day": busiest_day,
        "top_users": top_users,
        "top_voice": top_voice,
        "top_channels": top_channels,
    }

# ============================================================
# USER STATS
# ============================================================

async def get_user_stats(
    guild_id: int,
    user_id: int,
):
    # --------------------------------------------------------
    # Basic user statistics
    # --------------------------------------------------------

    user = await db.fetchone(
        """
        SELECT
            messages,
            characters,
            attachments,
            links,
            reactions_added,
            messages_edited,
            messages_deleted,
            typing_events,
            voice_sessions,
            voice_seconds,
            online_seconds,
            idle_seconds,
            last_text_channel_id,
            created_at,
            joined_at,
            first_seen,
            last_seen
        FROM users
        WHERE guild_id = %s
          AND user_id = %s
        """,
        (
            guild_id,
            user_id,
        ),
    )

    if not user:
        return None

    (
        messages,
        characters,
        attachments,
        links,
        reactions,
        edited,
        deleted,
        typing,
        voice_sessions,
        voice_seconds,
        online_seconds,
        idle_seconds,
        last_text_channel_id,
        created_at,
        joined_at,
        first_seen,
        last_seen,
    ) = user

    # --------------------------------------------------------
    # User rank
    # --------------------------------------------------------

    rank_row = await db.fetchone(
        """
        SELECT COUNT(*) + 1
        FROM users
        WHERE guild_id = %s
          AND messages > (
              SELECT messages
              FROM users
              WHERE guild_id = %s
                AND user_id = %s
          )
        """,
        (
            guild_id,
            guild_id,
            user_id,
        ),
    )

    rank = rank_row[0] if rank_row else 1

    # --------------------------------------------------------
    # Favorite channel
    # --------------------------------------------------------

    favorite_channel_row = await db.fetchone(
        """
        SELECT
            channel_id,
            COUNT(*) AS total
        FROM messages
        WHERE guild_id = %s
          AND user_id = %s
        GROUP BY channel_id
        ORDER BY total DESC
        LIMIT 1
        """,
        (
            guild_id,
            user_id,
        ),
    )

    favorite_channel = (
        favorite_channel_row[0]
        if favorite_channel_row
        else last_text_channel_id
    )

    # --------------------------------------------------------
    # Favorite hour
    # --------------------------------------------------------

    favorite_hour_row = await db.fetchone(
        """
        SELECT
            EXTRACT(HOUR FROM timestamp)::INT AS hour,
            COUNT(*) AS total
        FROM messages
        WHERE guild_id = %s
          AND user_id = %s
        GROUP BY hour
        ORDER BY total DESC
        LIMIT 1
        """,
        (
            guild_id,
            user_id,
        ),
    )

    favorite_hour = (
        favorite_hour_row[0]
        if favorite_hour_row
        else None
    )

    # --------------------------------------------------------
    # Days in server
    # --------------------------------------------------------

    days_in_server = None

    if joined_at:
        days_in_server = max(
            0,
            (now() - joined_at).days,
        )

    return {
        "messages": messages or 0,
        "characters": characters or 0,
        "rank": rank,
        "attachments": attachments or 0,
        "links": links or 0,
        "reactions": reactions or 0,
        "edited": edited or 0,
        "deleted": deleted or 0,
        "typing": typing or 0,
        "voice_sessions": voice_sessions or 0,
        "voice_seconds": voice_seconds or 0,
        "online_seconds": online_seconds or 0,
        "idle_seconds": idle_seconds or 0,
        "favorite_channel": favorite_channel,
        "favorite_hour": favorite_hour,
        "joined_at": joined_at,
        "days_in_server": days_in_server,
        "created_at": created_at,
        "first_seen": first_seen,
        "last_seen": last_seen,
    }

async def start_voice_session(
    guild_id: int,
    user_id: int,
    channel_id: int,
    joined_at,
):
    await db.execute(
        """
        INSERT INTO voice_sessions (
            guild_id,
            user_id,
            channel_id,
            joined_at,
            duration_seconds
        )
        VALUES (%s, %s, %s, %s, 0)
        """,
        (
            guild_id,
            user_id,
            channel_id,
            joined_at,
        ),
    )

    await db.execute(
        """
        UPDATE users
        SET
            last_seen = %s,
            last_voice_channel_id = %s
        WHERE guild_id = %s
          AND user_id = %s
        """,
        (
            joined_at,
            channel_id,
            guild_id,
            user_id,
        ),
    )


async def end_voice_session(
    guild_id: int,
    user_id: int,
    left_at,
):
    await db.execute(
        """
        UPDATE voice_sessions
        SET
            left_at = %s,
            duration_seconds = GREATEST(
                0,
                EXTRACT(
                    EPOCH FROM (%s - joined_at)
                )::BIGINT
            )
        WHERE id = (
            SELECT id
            FROM voice_sessions
            WHERE guild_id = %s
              AND user_id = %s
              AND left_at IS NULL
            ORDER BY joined_at DESC
            LIMIT 1
        )
        """,
        (
            left_at,
            left_at,
            guild_id,
            user_id,
        ),
    )

    # Actualizamos el total acumulado del usuario.
    await db.execute(
        """
        UPDATE users
        SET
            voice_sessions = (
                SELECT COUNT(*)
                FROM voice_sessions
                WHERE guild_id = %s
                  AND user_id = %s
                  AND left_at IS NOT NULL
            ),
            voice_seconds = COALESCE((
                SELECT SUM(duration_seconds)
                FROM voice_sessions
                WHERE guild_id = %s
                  AND user_id = %s
            ), 0),
            last_seen = %s,
            last_voice_channel_id = NULL
        WHERE guild_id = %s
          AND user_id = %s
        """,
        (
            guild_id,
            user_id,
            guild_id,
            user_id,
            left_at,
            guild_id,
            user_id,
        ),
    )