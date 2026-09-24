from .database import db


TABLES = """
CREATE TABLE IF NOT EXISTS users (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    username TEXT,
    display_name TEXT,

    created_at TIMESTAMPTZ,
    joined_at TIMESTAMPTZ,

    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,

    messages BIGINT DEFAULT 0,
    characters BIGINT DEFAULT 0,

    attachments BIGINT DEFAULT 0,
    links BIGINT DEFAULT 0,

    reactions_added BIGINT DEFAULT 0,

    messages_deleted BIGINT DEFAULT 0,
    messages_edited BIGINT DEFAULT 0,

    typing_events BIGINT DEFAULT 0,

    voice_sessions BIGINT DEFAULT 0,
    voice_seconds BIGINT DEFAULT 0,

    online_seconds BIGINT DEFAULT 0,
    idle_seconds BIGINT DEFAULT 0,

    last_voice_channel_id BIGINT,
    last_text_channel_id BIGINT,

    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,

    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,

    timestamp TIMESTAMPTZ NOT NULL,

    characters BIGINT DEFAULT 0,
    attachments BIGINT DEFAULT 0,
    links BIGINT DEFAULT 0
);


CREATE TABLE IF NOT EXISTS member_events (
    id BIGSERIAL PRIMARY KEY,

    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    event TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL
);


CREATE TABLE IF NOT EXISTS voice_sessions (
    id BIGSERIAL PRIMARY KEY,

    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    channel_id BIGINT NOT NULL,

    joined_at TIMESTAMPTZ NOT NULL,
    left_at TIMESTAMPTZ,

    duration_seconds BIGINT DEFAULT 0
);


CREATE TABLE IF NOT EXISTS presence_sessions (
    id BIGSERIAL PRIMARY KEY,

    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    status TEXT NOT NULL,

    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,

    duration_seconds BIGINT DEFAULT 0
);


CREATE TABLE IF NOT EXISTS presence_events (
    id BIGSERIAL PRIMARY KEY,

    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    status TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL
);


CREATE TABLE IF NOT EXISTS reactions (
    id BIGSERIAL PRIMARY KEY,

    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    channel_id BIGINT,
    message_id BIGINT,

    emoji TEXT,
    timestamp TIMESTAMPTZ NOT NULL
);


CREATE TABLE IF NOT EXISTS message_edits (
    id BIGSERIAL PRIMARY KEY,

    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    channel_id BIGINT,
    message_id BIGINT,

    timestamp TIMESTAMPTZ NOT NULL
);


CREATE TABLE IF NOT EXISTS message_deletions (
    id BIGSERIAL PRIMARY KEY,

    guild_id BIGINT NOT NULL,
    user_id BIGINT,

    channel_id BIGINT,
    message_id BIGINT,

    timestamp TIMESTAMPTZ NOT NULL
);
"""


INDEXES = """
CREATE INDEX IF NOT EXISTS idx_messages_guild_user
ON messages(guild_id, user_id);

CREATE INDEX IF NOT EXISTS idx_messages_timestamp
ON messages(timestamp);

CREATE INDEX IF NOT EXISTS idx_voice_guild_user
ON voice_sessions(guild_id, user_id);

CREATE INDEX IF NOT EXISTS idx_presence_guild_user
ON presence_sessions(guild_id, user_id);

CREATE INDEX IF NOT EXISTS idx_member_events_guild_user
ON member_events(guild_id, user_id);

CREATE INDEX IF NOT EXISTS idx_reactions_guild_user
ON reactions(guild_id, user_id);
"""


EXPECTED_TABLES = {
    "users",
    "messages",
    "member_events",
    "voice_sessions",
    "presence_sessions",
    "presence_events",
    "reactions",
    "message_edits",
    "message_deletions",
}


async def init_schema():
    print("[STATS][DB] Checking schema...", flush=True)

    async with db.connection() as conn:
        async with conn.cursor() as cursor:

            for statement in TABLES.split(";"):
                statement = statement.strip()

                if statement:
                    await cursor.execute(statement)

            for statement in INDEXES.split(";"):
                statement = statement.strip()

                if statement:
                    await cursor.execute(statement)

    tables = await db.fetchall("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)

    table_names = {row[0] for row in tables}

    missing = EXPECTED_TABLES - table_names

    if missing:
        print(
            f"[STATS][DB] ⚠️ Missing tables: "
            f"{sorted(missing)}",
            flush=True,
        )
    else:
        print(
            "[STATS][DB] ✅ All tables exist",
            flush=True,
        )

    print("[STATS][DB] Schema ready", flush=True)