import traceback

import discord
from discord import app_commands

from .config import GUILD_ID
from .repository import (
    ensure_user,
    get_server_stats,
    get_user_stats,
)
from .utils import format_duration, now


def valid_guild(interaction: discord.Interaction) -> bool:
    return (
        interaction.guild is not None
        and interaction.guild.id == GUILD_ID
    )


@app_commands.command(
    name="stats",
    description="Estadísticas completas del servidor",
)
async def stats(interaction: discord.Interaction):
    if not valid_guild(interaction):
        await interaction.response.send_message(
            "❌ Este comando no está disponible aquí.",
            ephemeral=True,
        )
        return

    await interaction.response.defer()

    try:
        guild = interaction.guild

        data = await get_server_stats(guild.id)

        embed = discord.Embed(
            title=f"📊 Estadísticas — {guild.name}",
            description=(
                "Estadísticas recopiladas por el bot "
                "sobre la actividad del servidor."
            ),
            color=discord.Color.blurple(),
            timestamp=now(),
        )

        embed.add_field(
            name="👥 Miembros",
            value=f"{guild.member_count:,}",
            inline=True,
        )

        embed.add_field(
            name="🤖 Bots",
            value=f"{data['bots']:,}",
            inline=True,
        )

        embed.add_field(
            name="🟢 Usuarios activos",
            value=f"{data['active_users']:,}",
            inline=True,
        )

        embed.add_field(
            name="💬 Mensajes",
            value=f"{data['total_messages']:,}",
            inline=True,
        )

        embed.add_field(
            name="📅 Últimos 7 días",
            value=f"{data['weekly_messages']:,}",
            inline=True,
        )

        embed.add_field(
            name="📆 Últimos 30 días",
            value=f"{data['monthly_messages']:,}",
            inline=True,
        )

        embed.add_field(
            name="📝 Caracteres",
            value=f"{data['total_characters']:,}",
            inline=True,
        )

        embed.add_field(
            name="🎙️ Tiempo en voz",
            value=format_duration(data["total_voice"]),
            inline=True,
        )

        embed.add_field(
            name="📥 Entradas",
            value=f"{data['joins']:,}",
            inline=True,
        )

        embed.add_field(
            name="📤 Salidas",
            value=f"{data['leaves']:,}",
            inline=True,
        )

        print(
            "[DEBUG] busiest_hour:",
            repr(data["busiest_hour"]),
            type(data["busiest_hour"]),
            flush=True,
        )

        print(
            "[DEBUG] busiest_day:",
            repr(data["busiest_day"]),
            type(data["busiest_day"]),
            flush=True,
        )

        # -----------------------------------------------
        # HORA MÁS ACTIVA
        # -----------------------------------------------

        if data["busiest_hour"]:
            hour, total = data["busiest_hour"]

            embed.add_field(
                name="⏰ Hora más activa",
                value=(
                    f"{hour:02d}:00 "
                    f"({total:,} mensajes)"
                ),
                inline=False,
            )

        # -----------------------------------------------
        # DÍA MÁS ACTIVO
        # -----------------------------------------------

        if data["busiest_day"]:
            day, total = data["busiest_day"]

            days = {
                0: "Domingo",
                1: "Lunes",
                2: "Martes",
                3: "Miércoles",
                4: "Jueves",
                5: "Viernes",
                6: "Sábado",
            }

            embed.add_field(
                name="📅 Día más activo",
                value=(
                    f"{days.get(day, 'Desconocido')} "
                    f"({total:,} mensajes)"
                ),
                inline=False,
            )

        # -----------------------------------------------
        # TOP USUARIOS
        # -----------------------------------------------

        if data["top_users"]:
            ranking = []

            for position, row in enumerate(
                data["top_users"],
                start=1,
            ):
                user_id = row[0]
                messages = row[2]
                characters = row[3]

                member = guild.get_member(user_id)

                if member:
                    ranking.append(
                        f"**{position}.** "
                        f"{member.mention} — "
                        f"💬 {messages:,} "
                        f"· 📝 {characters:,}"
                    )

            if ranking:
                embed.add_field(
                    name="🏆 Usuarios más activos",
                    value="\n".join(ranking),
                    inline=False,
                )

        # -----------------------------------------------
        # TOP VOZ
        # -----------------------------------------------

        if data["top_voice"]:
            ranking = []

            for position, row in enumerate(
                data["top_voice"],
                start=1,
            ):
                member = guild.get_member(row[0])

                if member:
                    ranking.append(
                        f"**{position}.** "
                        f"{member.mention} — "
                        f"{format_duration(row[2])}"
                    )

            if ranking:
                embed.add_field(
                    name="🎙️ Más tiempo en voz",
                    value="\n".join(ranking),
                    inline=False,
                )

        # -----------------------------------------------
        # TOP CANALES
        # -----------------------------------------------

        if data["top_channels"]:
            ranking = []

            for position, row in enumerate(
                data["top_channels"],
                start=1,
            ):
                channel = guild.get_channel(row[0])

                if channel:
                    ranking.append(
                        f"**{position}.** "
                        f"{channel.mention} — "
                        f"{row[1]:,} mensajes"
                    )

            if ranking:
                embed.add_field(
                    name="💬 Canales más activos",
                    value="\n".join(ranking),
                    inline=False,
                )

        embed.set_footer(
            text="Sistema global de estadísticas"
        )

        await interaction.followup.send(
            embed=embed
        )

    except Exception as error:
        print(
            f"[STATS] /stats ERROR: "
            f"{type(error).__name__}: {error}",
            flush=True,
        )
        traceback.print_exc()

        await interaction.followup.send(
            "❌ Error generando las estadísticas.",
            ephemeral=True,
        )


@app_commands.command(
    name="userstats",
    description="Muestra las estadísticas de un usuario",
)
@app_commands.describe(
    member="Usuario del que quieres ver las estadísticas",
)
async def userstats(
    interaction: discord.Interaction,
    member: discord.Member | None = None,
):
    if not valid_guild(interaction):
        await interaction.response.send_message(
            "❌ Este comando no está disponible aquí.",
            ephemeral=True,
        )
        return

    member = member or interaction.user

    data = await get_user_stats(
        guild_id=interaction.guild.id,
        user_id=member.id,
    )

    if data is None:
        await interaction.followup.send(
            "No hay estadísticas para este usuario.",
            ephemeral=True,
        )
        return

    favorite_channel_id = interaction.guild.get_channel(data.get("favorite_channel"))

    if member.bot:
        await interaction.response.send_message(
            "❌ No se recopilan estadísticas de bots.",
            ephemeral=True,
        )
        return

    await interaction.response.defer()

    try:
        await ensure_user(member)

        data = await get_user_stats(
            guild_id=interaction.guild.id,
            user_id=member.id,
        )

        if data is None:
            await interaction.followup.send(
                "No hay estadísticas para este usuario.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"👤 Estadísticas de {member.display_name}",
            color=discord.Color.blurple(),
            timestamp=now(),
        )

        if member.avatar:
            embed.set_thumbnail(
                url=member.avatar.url
            )

        embed.add_field(
            name="💬 Mensajes",
            value=f"{data['messages']:,}",
            inline=True,
        )

        embed.add_field(
            name="📝 Caracteres",
            value=f"{data['characters']:,}",
            inline=True,
        )

        embed.add_field(
            name="🏆 Ranking",
            value=f"#{data['rank']}",
            inline=True,
        )

        embed.add_field(
            name="📎 Adjuntos",
            value=f"{data['attachments']:,}",
            inline=True,
        )

        embed.add_field(
            name="🔗 Enlaces",
            value=f"{data['links']:,}",
            inline=True,
        )

        embed.add_field(
            name="😀 Reacciones",
            value=f"{data['reactions']:,}",
            inline=True,
        )

        embed.add_field(
            name="✏️ Editados",
            value=f"{data['edited']:,}",
            inline=True,
        )

        embed.add_field(
            name="🗑️ Borrados",
            value=f"{data['deleted']:,}",
            inline=True,
        )

        embed.add_field(
            name="⌨️ Escritura",
            value=f"{data['typing']:,}",
            inline=True,
        )

        embed.add_field(
            name="🎙️ Sesiones de voz",
            value=f"{data['voice_sessions']:,}",
            inline=True,
        )

        embed.add_field(
            name="🔊 Tiempo en voz",
            value=format_duration(
                data["voice_seconds"]
            ),
            inline=True,
        )

        embed.add_field(
            name="🟢 Tiempo online",
            value=format_duration(
                data["online_seconds"]
            ),
            inline=True,
        )

        embed.add_field(
            name="💤 Tiempo idle",
            value=format_duration(
                data["idle_seconds"]
            ),
            inline=True,
        )

        embed.add_field(
            name="📢 Canal favorito",
            value=favorite_channel_id,
            inline=False,
        )

        embed.add_field(
            name="⏰ Hora favorita",
            value=data["favorite_hour"],
            inline=True,
        )

        # -----------------------------------------------
        # FECHAS
        # -----------------------------------------------

        if data["joined_at"]:
            joined_timestamp = int(
                data["joined_at"].timestamp()
            )

            embed.add_field(
                name="📥 Entró al servidor",
                value=(
                    f"<t:{joined_timestamp}:D>\n"
                    f"({data['days_in_server']:,} días)"
                ),
                inline=True,
            )

        if data["created_at"]:
            created_timestamp = int(
                data["created_at"].timestamp()
            )

            embed.add_field(
                name="🆔 Cuenta creada",
                value=f"<t:{created_timestamp}:D>",
                inline=True,
            )

        if data["last_seen"]:
            last_seen_timestamp = int(
                data["last_seen"].timestamp()
            )

            embed.add_field(
                name="👀 Última actividad",
                value=f"<t:{last_seen_timestamp}:R>",
                inline=True,
            )

        # -----------------------------------------------
        # ROLES
        # -----------------------------------------------

        roles = [
            role.mention
            for role in member.roles
            if role != interaction.guild.default_role
        ]

        if roles:
            roles_text = ", ".join(roles)

            if len(roles_text) > 1000:
                roles_text = roles_text[:997] + "..."

            embed.add_field(
                name="🏷️ Roles",
                value=roles_text,
                inline=False,
            )

        embed.set_footer(
            text="Estadísticas individuales"
        )

        await interaction.followup.send(
            embed=embed
        )

    except Exception as error:
        print(
            f"[USERSTATS] ERROR: "
            f"{type(error).__name__}: {error}",
            flush=True,
        )

        await interaction.followup.send(
            "❌ Error generando las estadísticas.",
            ephemeral=True,
        )