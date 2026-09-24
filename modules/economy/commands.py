from decimal import Decimal

import discord

from .config import (
    CURRENCY,
    CURRENCY_SYMBOL,
    STARTING_BALANCE,
    VOICE_ACTIVITY_INTERVAL,
    VOICE_IGNORE_AFK,
    VOICE_REQUIRE_OTHERS,
    VOICE_REWARD_PER_MINUTE,
)
from .repository import (
    get_balance,
    get_voice_stats,
    transfer_money,
    get_leaderboard,
)
from .utils import (
    format_duration,
    format_money,
    now,
)


async def balance(
    interaction: discord.Interaction,
    member: discord.Member = None,
):
    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ Este comando solo funciona en un servidor.",
            ephemeral=True,
        )
        return

    if member is None:
        member = interaction.user

    if member.bot:
        await interaction.response.send_message(
            "❌ Los bots no tienen cuentas.",
            ephemeral=True,
        )
        return

    user_balance = await get_balance(
        interaction.guild.id,
        member.id,
    )

    voice_stats = await get_voice_stats(
        interaction.guild.id,
        member.id,
    )

    if voice_stats:
        total_seconds = voice_stats[0]
        total_earned = Decimal(str(voice_stats[1]))
    else:
        total_seconds = 0
        total_earned = Decimal("0")

    embed = discord.Embed(
        title="💰 Saldo",
        color=discord.Color.gold(),
        timestamp=now(),
    )

    embed.set_author(
        name=member.display_name,
        icon_url=member.display_avatar.url,
    )

    embed.add_field(
        name=f"{CURRENCY_SYMBOL} Saldo",
        value=format_money(user_balance),
        inline=False,
    )

    embed.add_field(
        name="🎙️ Tiempo en voz",
        value=format_duration(total_seconds),
        inline=True,
    )

    embed.add_field(
        name="💸 Ganado en voz",
        value=format_money(total_earned),
        inline=True,
    )

    embed.set_footer(
        text=f"Economía de {interaction.guild.name}",
    )

    await interaction.response.send_message(
        embed=embed,
    )


async def pay(
    interaction: discord.Interaction,
    member: discord.Member,
    amount: int,
):
    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ Este comando solo funciona en un servidor.",
            ephemeral=True,
        )
        return

    sender = interaction.user

    if sender.bot:
        await interaction.response.send_message(
            "❌ Los bots no pueden utilizar la economía.",
            ephemeral=True,
        )
        return

    if member.bot:
        await interaction.response.send_message(
            "❌ No puedes enviar monedas a un bot.",
            ephemeral=True,
        )
        return

    if amount <= 0:
        await interaction.response.send_message(
            "❌ La cantidad debe ser mayor que 0.",
            ephemeral=True,
        )
        return

    success, error = await transfer_money(
        interaction.guild.id,
        sender.id,
        member.id,
        amount,
    )

    if not success:
        await interaction.response.send_message(
            f"❌ {error}",
            ephemeral=True,
        )
        return

    sender_balance = await get_balance(
        interaction.guild.id,
        sender.id,
    )

    embed = discord.Embed(
        title="💸 Transferencia realizada",
        description=(
            f"{sender.mention} ha enviado "
            f"**{format_money(amount)}** a "
            f"{member.mention}."
        ),
        color=discord.Color.green(),
        timestamp=now(),
    )

    embed.add_field(
        name="💰 Tu saldo",
        value=format_money(sender_balance),
        inline=False,
    )

    await interaction.response.send_message(
        embed=embed,
    )


async def leaderboard(
    interaction: discord.Interaction,
):
    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ Este comando solo funciona en un servidor.",
            ephemeral=True,
        )
        return

    rows = await get_leaderboard(
        interaction.guild.id,
        10,
    )

    if not rows:
        await interaction.response.send_message(
            "📊 Todavía no hay cuentas.",
            ephemeral=True,
        )
        return

    ranking = []

    position_emojis = {
        1: "🥇",
        2: "🥈",
        3: "🥉",
    }

    for position, (user_id, user_balance) in enumerate(
        rows,
        start=1,
    ):
        member = interaction.guild.get_member(
            user_id
        )

        name = (
            member.mention
            if member
            else f"<@{user_id}>"
        )

        medal = position_emojis.get(
            position,
            f"**{position}.**",
        )

        ranking.append(
            f"{medal} {name} — "
            f"**{format_money(user_balance)}**"
        )

    embed = discord.Embed(
        title="🏆 Ranking económico",
        description="\n".join(ranking),
        color=discord.Color.gold(),
        timestamp=now(),
    )

    embed.set_footer(
        text=f"Top 10 — {interaction.guild.name}",
    )

    await interaction.response.send_message(
        embed=embed,
    )


async def economyinfo(
    interaction: discord.Interaction,
):
    embed = discord.Embed(
        title=f"{CURRENCY_SYMBOL} Economía",
        description=(
            "Sistema económico basado "
            "en actividad en canales de voz."
        ),
        color=discord.Color.gold(),
    )

    embed.add_field(
        name="Moneda",
        value=f"{CURRENCY_SYMBOL} {CURRENCY}",
        inline=True,
    )

    embed.add_field(
        name="🎙️ Recompensa",
        value=(
            f"{format_money(VOICE_REWARD_PER_MINUTE)} "
            "/ minuto"
        ),
        inline=True,
    )

    embed.add_field(
        name="⏱️ Comprobación",
        value=f"Cada {VOICE_ACTIVITY_INTERVAL}s",
        inline=True,
    )

    embed.add_field(
        name="👥 Requiere otra persona",
        value=(
            "Sí"
            if VOICE_REQUIRE_OTHERS
            else "No"
        ),
        inline=True,
    )

    embed.add_field(
        name="💤 Canal AFK",
        value=(
            "Ignorado"
            if VOICE_IGNORE_AFK
            else "Cuenta"
        ),
        inline=True,
    )

    embed.add_field(
        name=f"{CURRENCY_SYMBOL} Saldo inicial",
        value=format_money(STARTING_BALANCE),
        inline=True,
    )

    await interaction.response.send_message(
        embed=embed,
    )