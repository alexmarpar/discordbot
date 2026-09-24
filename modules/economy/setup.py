import discord

from .config import GUILD_ID
from .database import db
from .schema import init_schema

from .events import (
    on_ready,
    on_voice_state_update,
    setup_events,
)

from .commands import (
    balance,
    pay,
    leaderboard,
    economyinfo,
)


GUILD = discord.Object(id=GUILD_ID)


_initialized = False


async def economy_on_ready():
    global _initialized

    if _initialized:
        return

    print(
        "[ECONOMY] Inicializando módulo...",
        flush=True,
    )

    await db.connect()
    await init_schema()

    _initialized = True

    print(
        "[ECONOMY] Módulo listo",
        flush=True,
    )

    await on_ready()


def setup_economy(client: discord.Client):
    print(
        "[ECONOMY] Registrando módulo...",
        flush=True,
    )

    setup_events(client)

    # ========================================================
    # /BALANCE
    # ========================================================

    client.tree.add_command(
        discord.app_commands.Command(
            name="balance",
            description=(
                "Muestra el saldo y actividad "
                "de un usuario"
            ),
            callback=balance,
        ),
        guild=GUILD,
    )

    # ========================================================
    # /PAY
    # ========================================================

    client.tree.add_command(
        discord.app_commands.Command(
            name="pay",
            description="Envía monedas a otro usuario",
            callback=pay,
        ),
        guild=GUILD,
    )

    # ========================================================
    # /LEADERBOARD
    # ========================================================

    client.tree.add_command(
        discord.app_commands.Command(
            name="leaderboard",
            description="Muestra el ranking económico",
            callback=leaderboard,
        ),
        guild=GUILD,
    )

    # ========================================================
    # /ECONOMYINFO
    # ========================================================

    client.tree.add_command(
        discord.app_commands.Command(
            name="economyinfo",
            description="Muestra la configuración de la economía",
            callback=economyinfo,
        ),
        guild=GUILD,
    )

    # ========================================================
    # READY
    # ========================================================

    client.add_listener(
        economy_on_ready,
        "on_ready",
    )

    # ========================================================
    # VOICE STATE UPDATE
    # ========================================================

    client.add_listener(
        on_voice_state_update,
        "on_voice_state_update",
    )

    print(
        "[ECONOMY] Module registered successfully",
        flush=True,
    )