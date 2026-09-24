import discord
from discord import app_commands
from decimal import Decimal

from .config import GUILD, CURRENCY_NAME, CURRENCY_SYMBOL
from .repository import (
    get_shop_items,
    buy_item,
    get_inventory,
    create_shop_item,
    delete_shop_item,
    update_shop_item,
)
from .utils import format_money


# ============================================================
# /shop
# ============================================================
async def shop_command(interaction: discord.Interaction):
    try:
        items = await get_shop_items(interaction.guild.id)

        if not items:
            await interaction.response.send_message(
                "🛒 La tienda está vacía."
            )
            return

        embed = discord.Embed(
            title="🛒 Tienda",
            description="Usa `/buy <nombre>` para comprar un artículo.",
        )

        for item in items:
            item_id, name, description, price, stock, role_id, max_quantity = item

            if stock == -1:
                stock_text = "♾️ Ilimitado"
            else:
                stock_text = f"📦 {stock}"

            if max_quantity == -1:
                limit_text = "♾️ Sin límite"
            else:
                limit_text = f"Máx. {max_quantity} por usuario"

            role_text = f"<@&{role_id}>" if role_id else "Sin rol"

            embed.add_field(
                name=f"{name} — {format_money(price)} {CURRENCY_SYMBOL}",
                value=(
                    f"{description or 'Sin descripción'}\n"
                    f"{stock_text} · {limit_text}\n"
                    f"🎭 {role_text}"
                ),
                inline=False,
            )

        await interaction.response.send_message(embed=embed)

    except Exception as error:
        print(f"[SHOP] ERROR en /shop: {type(error).__name__}: {error}")

        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Ha ocurrido un error al cargar la tienda.",
                ephemeral=True,
            )


# ============================================================
# /buy
# ============================================================
async def buy_command(
    interaction: discord.Interaction,
    name: str,
    quantity: int = 1,
):
    if quantity < 1:
        await interaction.response.send_message(
            "❌ La cantidad debe ser mayor que 0.",
            ephemeral=True,
        )
        return

    try:
        result = await buy_item(
            guild_id=interaction.guild.id,
            user_id=interaction.user.id,
            item_name=name,
            quantity=quantity,
        )

        if not result.success:
            await interaction.response.send_message(
                f"❌ {result.message}",
                ephemeral=True,
            )
            return

        # Añadir rol después de completar la compra.
        if result.role_id:
            role = interaction.guild.get_role(result.role_id)

            if role:
                try:
                    await interaction.user.add_roles(role)
                except discord.Forbidden:
                    print(
                        f"[SHOP] No se pudo añadir el rol "
                        f"{result.role_id} a {interaction.user.id}"
                    )

        await interaction.response.send_message(
            f"✅ Has comprado **{quantity}x {result.item_name}** "
            f"por **{format_money(result.total)} {CURRENCY_SYMBOL}**."
        )

    except Exception as error:
        print(
            f"[SHOP] ERROR en /buy: "
            f"{type(error).__name__}: {error}"
        )

        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Ha ocurrido un error al realizar la compra.",
                ephemeral=True,
            )
            
async def shop_command(interaction: discord.Interaction):
    try:
        items = await get_shop_items(interaction.guild.id)

        if not items:
            await interaction.response.send_message(
                "🛒 La tienda está vacía."
            )
            return

        embed = discord.Embed(
            title="🛒 Tienda",
            description="Usa `/buy <nombre>` para comprar un artículo.",
        )

        for item in items:
            item_id, name, description, price, stock, role_id, max_quantity = item

            if stock == -1:
                stock_text = "♾️ Ilimitado"
            else:
                stock_text = f"📦 {stock}"

            if max_quantity == -1:
                limit_text = "♾️ Sin límite"
            else:
                limit_text = f"Máx. {max_quantity} por usuario"

            role_text = f"<@&{role_id}>" if role_id else "Sin rol"

            embed.add_field(
                name=f"{name} — {format_money(price)} {CURRENCY_SYMBOL}",
                value=(
                    f"{description or 'Sin descripción'}\n"
                    f"{stock_text} · {limit_text}\n"
                    f"🎭 {role_text}"
                ),
                inline=False,
            )

        await interaction.response.send_message(embed=embed)

    except Exception as error:
        print(f"[SHOP] ERROR en /shop: {type(error).__name__}: {error}")

        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Ha ocurrido un error al cargar la tienda.",
                ephemeral=True,
            )


# ============================================================
# /buy
# ============================================================

async def buy_command(
    interaction: discord.Interaction,
    name: str,
    quantity: int = 1,
):
    if quantity < 1:
        await interaction.response.send_message(
            "❌ La cantidad debe ser mayor que 0.",
            ephemeral=True,
        )
        return

    try:
        result = await buy_item(
            guild_id=interaction.guild.id,
            user_id=interaction.user.id,
            item_name=name,
            quantity=quantity,
        )

        if not result.success:
            await interaction.response.send_message(
                f"❌ {result.message}",
                ephemeral=True,
            )
            return

        # El rol se añade fuera de la transacción de PostgreSQL.
        if result.role_id:
            role = interaction.guild.get_role(result.role_id)

            if role:
                try:
                    await interaction.user.add_roles(role)
                except discord.Forbidden:
                    print(
                        f"[SHOP] No se pudo añadir el rol "
                        f"{result.role_id} a {interaction.user.id}"
                    )

        await interaction.response.send_message(
            f"✅ Has comprado **{quantity}x {result.item_name}** "
            f"por **{format_money(result.total)} {CURRENCY_SYMBOL}**."
        )

    except Exception as error:
        print(f"[SHOP] ERROR en /buy: {type(error).__name__}: {error}")

        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Ha ocurrido un error al realizar la compra.",
                ephemeral=True,
            )


# ============================================================
# /inventory
# ============================================================

async def inventory_command(interaction: discord.Interaction):
    try:
        items = await get_inventory(
            interaction.guild.id,
            interaction.user.id,
        )

        if not items:
            await interaction.response.send_message(
                "🎒 Tu inventario está vacío.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"🎒 Inventario de {interaction.user.display_name}"
        )

        for name, description, quantity in items:
            embed.add_field(
                name=f"{name} × {quantity}",
                value=description or "Sin descripción",
                inline=False,
            )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )

    except Exception as error:
        print(
            f"[SHOP] ERROR en /inventory: "
            f"{type(error).__name__}: {error}"
        )

        await interaction.response.send_message(
            "❌ No se pudo cargar tu inventario.",
            ephemeral=True,
        )


# ============================================================
# /shopinfo
# ============================================================

async def shopinfo_command(interaction: discord.Interaction):
    try:
        items = await get_shop_items(interaction.guild.id)

        await interaction.response.send_message(
            f"🛒 La tienda tiene **{len(items)} artículos**."
        )

    except Exception as error:
        print(
            f"[SHOP] ERROR en /shopinfo: "
            f"{type(error).__name__}: {error}"
        )

        await interaction.response.send_message(
            "❌ No se pudo obtener la información de la tienda.",
            ephemeral=True,
        )


# ============================================================
# ADMIN CHECK
# ============================================================

def is_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.administrator


# ============================================================
# /shop_add
# ============================================================

async def shop_add_command(
    interaction: discord.Interaction,
    name: str,
    price: float,
    stock: int = -1,
    description: str | None = None,
    role_id: str | None = None,
    max_quantity_per_user: int = -1,
):
    if not is_admin(interaction):
        await interaction.response.send_message(
            "❌ Necesitas permisos de administrador.",
            ephemeral=True,
        )
        return

    if price < 0:
        await interaction.response.send_message(
            "❌ El precio no puede ser negativo.",
            ephemeral=True,
        )
        return

    if stock < -1:
        await interaction.response.send_message(
            "❌ El stock debe ser `-1` o mayor.",
            ephemeral=True,
        )
        return

    if max_quantity_per_user != -1 and max_quantity_per_user <= 0:
        await interaction.response.send_message(
            "❌ El límite debe ser `-1` o mayor que 0.",
            ephemeral=True,
        )
        return

    parsed_role_id = int(role_id) if role_id else None

    try:
        await create_shop_item(
            guild_id=interaction.guild.id,
            name=name,
            description=description,
            price=Decimal(str(price)),
            stock=stock,
            role_id=parsed_role_id,
            max_quantity_per_user=max_quantity_per_user,
        )

        await interaction.response.send_message(
            f"✅ Artículo **{name}** añadido a la tienda."
        )

    except Exception as error:
        print(
            f"[SHOP] ERROR en /shop_add: "
            f"{type(error).__name__}: {error}"
        )

        await interaction.response.send_message(
            "❌ No se pudo añadir el artículo.",
            ephemeral=True,
        )


# ============================================================
# /shop_remove
# ============================================================

async def shop_remove_command(
    interaction: discord.Interaction,
    name: str,
):
    if not is_admin(interaction):
        await interaction.response.send_message(
            "❌ Necesitas permisos de administrador.",
            ephemeral=True,
        )
        return

    try:
        deleted = await delete_shop_item(
            interaction.guild.id,
            name,
        )

        if not deleted:
            await interaction.response.send_message(
                f"❌ No existe ningún artículo llamado **{name}**.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ Artículo **{name}** eliminado."
        )

    except Exception as error:
        print(
            f"[SHOP] ERROR en /shop_remove: "
            f"{type(error).__name__}: {error}"
        )

        await interaction.response.send_message(
            "❌ No se pudo eliminar el artículo.",
            ephemeral=True,
        )


# ============================================================
# /shop_edit
# ============================================================

async def shop_edit_command(
    interaction: discord.Interaction,
    name: str,
    price: float | None = None,
    stock: int | None = None,
    description: str | None = None,
    role_id: str | None = None,
    max_quantity_per_user: int | None = None,
):
    if not is_admin(interaction):
        await interaction.response.send_message(
            "❌ Necesitas permisos de administrador.",
            ephemeral=True,
        )
        return

    if price is not None and price < 0:
        await interaction.response.send_message(
            "❌ El precio no puede ser negativo.",
            ephemeral=True,
        )
        return

    if stock is not None and stock < -1:
        await interaction.response.send_message(
            "❌ El stock debe ser `-1` o mayor.",
            ephemeral=True,
        )
        return

    if (
        max_quantity_per_user is not None
        and max_quantity_per_user != -1
        and max_quantity_per_user <= 0
    ):
        await interaction.response.send_message(
            "❌ El límite debe ser `-1` o mayor que 0.",
            ephemeral=True,
        )
        return

    parsed_role_id = int(role_id) if role_id else None

    try:
        updated = await update_shop_item(
            guild_id=interaction.guild.id,
            name=name,
            price=Decimal(str(price)) if price is not None else None,
            stock=stock,
            description=description,
            role_id=parsed_role_id,
            max_quantity_per_user=max_quantity_per_user,
        )

        if not updated:
            await interaction.response.send_message(
                f"❌ No existe ningún artículo llamado **{name}**.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ Artículo **{name}** actualizado."
        )

    except Exception as error:
        print(
            f"[SHOP] ERROR en /shop_edit: "
            f"{type(error).__name__}: {error}"
        )

        await interaction.response.send_message(
            "❌ No se pudo editar el artículo.",
            ephemeral=True,
        )


# ============================================================
# REGISTER COMMANDS
# ============================================================

def setup_commands(client: discord.Client):
    client.tree.add_command(
        app_commands.Command(
            name="shop",
            description="Ver la tienda",
            callback=shop_command,
        ),
        guild=GUILD,
    )

    client.tree.add_command(
        app_commands.Command(
            name="buy",
            description="Comprar un artículo",
            callback=buy_command,
        ),
        guild=GUILD,
    )

    client.tree.add_command(
        app_commands.Command(
            name="inventory",
            description="Ver tu inventario",
            callback=inventory_command,
        ),
        guild=GUILD,
    )

    client.tree.add_command(
        app_commands.Command(
            name="shopinfo",
            description="Ver información de la tienda",
            callback=shopinfo_command,
        ),
        guild=GUILD,
    )

    client.tree.add_command(
        app_commands.Command(
            name="shop_add",
            description="Añadir un artículo a la tienda",
            callback=shop_add_command,
        ),
        guild=GUILD,
    )

    client.tree.add_command(
        app_commands.Command(
            name="shop_remove",
            description="Eliminar un artículo de la tienda",
            callback=shop_remove_command,
        ),
        guild=GUILD,
    )

    client.tree.add_command(
        app_commands.Command(
            name="shop_edit",
            description="Editar un artículo de la tienda",
            callback=shop_edit_command,
        ),
        guild=GUILD,
    )

    print("[SHOP] Comandos registrados", flush=True)