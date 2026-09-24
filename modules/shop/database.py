from psycopg_pool import AsyncConnectionPool

from .config import DATABASE_URL


class Database:

    def __init__(self):
        self.pool = None

    async def connect(self):

        if self.pool is not None:
            return

        print(
            "[SHOP][DB] Conectando a PostgreSQL...",
            flush=True
        )

        self.pool = AsyncConnectionPool(
            conninfo=DATABASE_URL,
            min_size=1,
            max_size=5,
            open=False
        )

        await self.pool.open()

        result = await self.fetchone(
            "SELECT 1"
        )

        if result != (1,):
            raise RuntimeError(
                "La conexión con PostgreSQL no respondió correctamente"
            )

        print(
            "[SHOP][DB] Conectado",
            flush=True
        )

    async def close(self):

        if self.pool is None:
            return

        await self.pool.close()
        self.pool = None

        print(
            "[SHOP][DB] Pool cerrado",
            flush=True
        )

    async def execute(
        self,
        query,
        params=()
    ):

        if self.pool is None:
            raise RuntimeError(
                "El pool de PostgreSQL no está inicializado"
            )

        async with self.pool.connection() as conn:

            async with conn.transaction():

                async with conn.cursor() as cursor:

                    await cursor.execute(
                        query,
                        params
                    )

    async def fetchone(
        self,
        query,
        params=()
    ):

        if self.pool is None:
            raise RuntimeError(
                "El pool de PostgreSQL no está inicializado"
            )

        async with self.pool.connection() as conn:

            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    params
                )

                return await cursor.fetchone()

    async def fetchall(
        self,
        query,
        params=()
    ):

        if self.pool is None:
            raise RuntimeError(
                "El pool de PostgreSQL no está inicializado"
            )

        async with self.pool.connection() as conn:

            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    params
                )

                return await cursor.fetchall()


db = Database()