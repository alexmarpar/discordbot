from .database import db
from .schema import init_schema


_initialized = False


async def on_ready():

    global _initialized

    if _initialized:
        return

    print(
        "[SHOP] Inicializando módulo...",
        flush=True
    )

    try:
        await db.connect()
        await init_schema()

        _initialized = True

        print(
            "[SHOP] Módulo listo",
            flush=True
        )

    except Exception as error:

        print(
            f"[SHOP] ERROR inicializando: "
            f"{type(error).__name__}: {error}",
            flush=True
        )

        raise