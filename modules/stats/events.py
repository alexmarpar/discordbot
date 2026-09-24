import discord

from .config import GUILD_ID
from datetime import datetime, timezone
from .repository import (
    add_member_event,
    add_message,
    add_message_deletion,
    add_message_edit,
    add_reaction,
    add_typing_event,
    ensure_user,
    start_voice_session,
    end_voice_session,
)


def is_valid_guild(guild) -> bool:
    return (
        guild is not None
        and guild.id == GUILD_ID
    )


async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if not is_valid_guild(message.guild):
        return

    content = message.content or ""

    await ensure_user(message.author)

    await add_message(
        guild_id=message.guild.id,
        user_id=message.author.id,
        channel_id=message.channel.id,
        timestamp=message.created_at,
        characters=len(content),
        attachments=len(message.attachments),
        links=(
            content.count("http://")
            + content.count("https://")
        ),
    )


async def on_message_edit(
    before: discord.Message,
    after: discord.Message,
):
    if after.author.bot:
        return

    if not is_valid_guild(after.guild):
        return

    await add_message_edit(
        guild_id=after.guild.id,
        user_id=after.author.id,
        channel_id=after.channel.id,
        message_id=after.id,
    )


async def on_message_delete(
    message: discord.Message,
):
    if message.author.bot:
        return

    if not is_valid_guild(message.guild):
        return

    await add_message_deletion(
        guild_id=message.guild.id,
        user_id=message.author.id,
        channel_id=message.channel.id,
        message_id=message.id,
    )


async def on_raw_reaction_add(
    payload: discord.RawReactionActionEvent,
):
    if payload.guild_id != GUILD_ID:
        return

    guild = payload.member.guild if payload.member else None

    if guild is None:
        return

    member = guild.get_member(payload.user_id)

    if member is None or member.bot:
        return

    await ensure_user(member)

    await add_reaction(
        guild_id=payload.guild_id,
        user_id=payload.user_id,
        channel_id=payload.channel_id,
        message_id=payload.message_id,
        emoji=str(payload.emoji),
    )


async def on_typing(
    channel,
    user,
    when,
):
    if user.bot:
        return

    if not is_valid_guild(channel.guild):
        return

    await ensure_user(user)

    await add_typing_event(
        guild_id=channel.guild.id,
        user_id=user.id,
        channel_id=channel.id,
    )


async def on_member_join(member: discord.Member):
    if member.bot:
        return

    if not is_valid_guild(member.guild):
        return

    await ensure_user(member)

    await add_member_event(
        guild_id=member.guild.id,
        user_id=member.id,
        event="join",
    )


async def on_member_remove(member: discord.Member):
    if not is_valid_guild(member.guild):
        return

    await add_member_event(
        guild_id=member.guild.id,
        user_id=member.id,
        event="leave",
    )

async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState,
):
    if member.bot:
        return

    if not is_valid_guild(member.guild):
        return

    # No ha cambiado el canal de voz.
    if before.channel == after.channel:
        return

    # Aseguramos que el usuario existe.
    await ensure_user(member)

    # ========================================================
    # ENTRA EN VOZ
    # ========================================================

    if before.channel is None and after.channel is not None:
        await start_voice_session(
            guild_id=member.guild.id,
            user_id=member.id,
            channel_id=after.channel.id,
            joined_at=datetime.now(timezone.utc),
        )

    # ========================================================
    # SALE DE VOZ
    # ========================================================

    elif before.channel is not None and after.channel is None:
        await end_voice_session(
            guild_id=member.guild.id,
            user_id=member.id,
            left_at=datetime.now(timezone.utc),
        )

    # ========================================================
    # CAMBIA DE CANAL
    # ========================================================

    elif before.channel is not None and after.channel is not None:
        await end_voice_session(
            guild_id=member.guild.id,
            user_id=member.id,
            left_at=datetime.now(timezone.utc),
        )

        await start_voice_session(
            guild_id=member.guild.id,
            user_id=member.id,
            channel_id=after.channel.id,
            joined_at=datetime.now(timezone.utc),
        )