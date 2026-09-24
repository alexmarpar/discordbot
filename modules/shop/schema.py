from .database import db


EXPECTED_TABLES = {
    "shop_items",
    "inventory",
}


async def init_schema():

    print(
        "[SHOP][DB] Comprobando schema...",
        flush=True
    )

    async with db.pool.connection() as conn:

        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS shop_items (

                    id BIGSERIAL PRIMARY KEY,

                    guild_id BIGINT NOT NULL,

                    name TEXT NOT NULL,

                    description TEXT,

                    price NUMERIC(20, 2)
                        NOT NULL
                        DEFAULT 0
                        CHECK (price >= 0),

                    stock INTEGER
                        NOT NULL
                        DEFAULT -1
                        CHECK (stock >= -1),

                    role_id BIGINT,

                    created_at TIMESTAMPTZ
                        NOT NULL
                        DEFAULT NOW()
                )
                """
            )

            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory (

                    guild_id BIGINT NOT NULL,

                    user_id BIGINT NOT NULL,

                    item_id BIGINT NOT NULL,

                    quantity INTEGER
                        NOT NULL
                        DEFAULT 0
                        CHECK (quantity >= 0),

                    created_at TIMESTAMPTZ
                        NOT NULL
                        DEFAULT NOW(),

                    updated_at TIMESTAMPTZ
                        NOT NULL
                        DEFAULT NOW(),

                    PRIMARY KEY (
                        guild_id,
                        user_id,
                        item_id
                    ),

                    CONSTRAINT fk_inventory_item

                        FOREIGN KEY (item_id)

                        REFERENCES shop_items(id)

                        ON DELETE CASCADE
                )
                """
            )

            await cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_shop_items_guild

                ON shop_items(
                    guild_id
                )
                """
            )

            await cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_shop_items_guild_name

                ON shop_items(
                    guild_id,
                    LOWER(name)
                )
                """
            )

            await cursor.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS
                idx_shop_items_unique_name

                ON shop_items(
                    guild_id,
                    LOWER(name)
                )
                """
            )

            await cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_inventory_user

                ON inventory(
                    guild_id,
                    user_id
                )
                """
            )

    tables = await db.fetchall(
        """
        SELECT table_name

        FROM information_schema.tables

        WHERE table_schema = 'public'

        AND table_type = 'BASE TABLE'

        ORDER BY table_name
        """
    )

    table_names = {
        row[0]
        for row in tables
    }

    missing = EXPECTED_TABLES - table_names

    if missing:

        print(
            f"[SHOP][DB] ⚠️ Missing tables: "
            f"{sorted(missing)}",
            flush=True
        )

    else:

        print(
            "[SHOP][DB] ✅ All tables exist",
            flush=True
        )

    print(
        "[SHOP][DB] Schema listo",
        flush=True
    )