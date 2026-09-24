import discord
from discord import app_commands

from .config import GUILD_ID
from .events import on_ready

from .commands import (
    shop_command,
    buy_command,
    inventory_command,
    shop_info_command,
    shop_add_command,
    shop_remove_command,
    shop_edit_command,
)


GUILD = discord.Object(
    id=GUILD_ID
)


def setup_shop(client: discord.Client):

    client.tree.add_command(
        app_commands.Command(
            name="shop",
            description="Muestra los productos de la tienda.",
            callback=shop_command
        ),
        guild=GUILD
    )

    client.tree.add_command(
        app_commands.Command(
            name="buy",
            description="Compra un producto de la tienda.",
            callback=buy_command
        ),
        guild=GUILD
    )

    client.tree.add_command(
        app_commands.Command(
            name="inventory",
            description="Muestra tu inventario.",
            callback=inventory_command
        ),
        guild=GUILD
    )

    client.tree.add_command(
        app_commands.Command(
            name="shopinfo",
            description="Muestra información de la tienda.",
            callback=shop_info_command
        ),
        guild=GUILD
    )

    client.tree.add_command(
        app_commands.Command(
            name="shop_add",
            description="Crea un producto en la tienda.",
            callback=shop_add_command
        ),
        guild=GUILD
    )

    client.tree.add_command(
        app_commands.Command(
            name="shop_remove",
            description="Elimina un producto de la tienda.",
            callback=shop_remove_command
        ),
        guild=GUILD
    )

    client.tree.add_command(
        app_commands.Command(
            name="shop_edit",
            description="Edita un producto de la tienda.",
            callback=shop_edit_command
        ),
        guild=GUILD
    )

    client.add_listener(
        on_ready,
        "on_ready"
    )

    print(
        "[SHOP] Módulo registrado correctamente",
        flush=True
    )