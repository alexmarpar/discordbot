import os

from dotenv import load_dotenv
from psycopg_pool import AsyncConnectionPool
from .config import DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not defined")


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if self.pool is not None:
            return

        self.pool = AsyncConnectionPool(
            conninfo=DATABASE_URL,
            min_size=1,
            max_size=5,
            open=False,
        )

        await self.pool.open()

    async def close(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def execute(self, query, params=()):
        async with self.pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)

    async def fetchone(self, query, params=()):
        async with self.pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchone()

    async def fetchall(self, query, params=()):
        async with self.pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchall()


db = Database()