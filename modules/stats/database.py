from contextlib import asynccontextmanager

from psycopg_pool import AsyncConnectionPool

from .config import DATABASE_URL


class Database:
    def __init__(self):
        self.pool: AsyncConnectionPool | None = None

    async def connect(self):
        if self.pool is not None:
            return

        print("[STATS][DB] Connecting to PostgreSQL...", flush=True)

        self.pool = AsyncConnectionPool(
            conninfo=DATABASE_URL,
            open=False,
        )

        await self.pool.open()

        async with self.pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT
                        current_database(),
                        current_schema()
                """)

                database, schema = await cursor.fetchone()

        print("[STATS][DB] Connected to PostgreSQL correctly", flush=True)
        print(f"[STATS][DB] Database: {database}", flush=True)
        print(f"[STATS][DB] Schema: {schema}", flush=True)

    async def close(self):
        if self.pool is None:
            return

        await self.pool.close()
        self.pool = None

        print("[STATS][DB] Pool closed", flush=True)

    def _check_pool(self):
        if self.pool is None:
            raise RuntimeError(
                "The connection pool is not initialized. Call 'connect()' first."
            )

    @asynccontextmanager
    async def connection(self):
        self._check_pool()

        async with self.pool.connection() as conn:
            yield conn

    @asynccontextmanager
    async def transaction(self):
        self._check_pool()

        async with self.pool.connection() as conn:
            async with conn.transaction():
                yield conn

    async def execute(
        self,
        query: str,
        params=(),
    ):
        async with self.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)

    async def fetchone(
        self,
        query: str,
        params=(),
    ):
        async with self.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchone()

    async def fetchall(
        self,
        query: str,
        params=(),
    ):
        async with self.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchall()


db = Database()