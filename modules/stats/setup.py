import discord

from .config import GUILD_ID
from .database import db
from .schema import init_schema

from .events import (
    on_message,
    on_message_edit,
    on_message_delete,
    on_raw_reaction_add,
    on_typing,
    on_member_join,
    on_member_remove,
    on_voice_state_update,
)

from .commands import (
    stats,
    userstats,
)


GUILD = discord.Object(id=GUILD_ID)


_initialized = False


async def on_ready():
    global _initialized

    if _initialized:
        return

    print("[STATS] Inicializando módulo...", flush=True)

    await db.connect()
    await init_schema()

    _initialized = True

    print("[STATS] Módulo listo", flush=True)


def setup_stats(client: discord.Client):
    print("[STATS] Registrando módulo...", flush=True)

    client.tree.add_command(
        stats,
        guild=GUILD,
    )

    client.tree.add_command(
        userstats,
        guild=GUILD,
    )

    client.add_listener(
        on_ready,
        "on_ready",
    )

    client.add_listener(
        on_message,
        "on_message",
    )

    client.add_listener(
        on_message_edit,
        "on_message_edit",
    )

    client.add_listener(
        on_message_delete,
        "on_message_delete",
    )

    client.add_listener(
        on_raw_reaction_add,
        "on_raw_reaction_add",
    )

    client.add_listener(
        on_typing,
        "on_typing",
    )

    client.add_listener(
        on_member_join,
        "on_member_join",
    )

    client.add_listener(
        on_member_remove,
        "on_member_remove",
    )
    client.add_listener(
            on_voice_state_update,
            "on_voice_state_update",
        )

    print(
        "[STATS] Module registered successfully",
        flush=True,
    )