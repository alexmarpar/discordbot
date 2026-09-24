import asyncio
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN

import discord

from .config import (
    GUILD_ID,
    VOICE_IGNORE_AFK,
    VOICE_REQUIRE_OTHERS,
    VOICE_REWARD_PER_MINUTE,
    VOICE_ACTIVITY_INTERVAL,
)
from .repository import (
    get_active_voice_sessions,
    get_voice_session,
    start_voice_session,
    delete_voice_session,
    update_voice_session,
    add_voice_time,
)
from .utils import now, parse_time


_client = None
_voice_task = None


def setup_events(client):
    global _client

    _client = client


def user_counts_for_voice(
    member: discord.Member,
):
    if member.bot:
        return False

    voice_state = member.voice

    if voice_state is None:
        return False

    channel = voice_state.channel

    if channel is None:
        return False

    if (
        VOICE_IGNORE_AFK
        and member.guild.afk_channel
        and channel.id == member.guild.afk_channel.id
    ):
        return False

    if voice_state.deaf or voice_state.self_deaf:
        return False

    if VOICE_REQUIRE_OTHERS:

        humans = [
            member
            for member in channel.members
            if not member.bot
        ]

        if len(humans) < 2:
            return False

    return True


async def process_voice_reward(
    guild_id: int,
    user_id: int,
    last_paid_at,
):
    last_paid_at = parse_time(last_paid_at)

    if last_paid_at is None:
        last_paid_at = now()

    elapsed = int(
        (now() - last_paid_at).total_seconds()
    )

    if elapsed < 60:
        return

    complete_minutes = elapsed // 60
    seconds_to_process = complete_minutes * 60

    reward = (
        VOICE_REWARD_PER_MINUTE
        * Decimal(complete_minutes)
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_DOWN,
    )

    success = await add_voice_time(
        guild_id,
        user_id,
        seconds_to_process,
        reward,
    )

    if not success:
        return

    new_last_paid = (
        last_paid_at.timestamp()
        + seconds_to_process
    )

    new_last_paid_at = datetime.fromtimestamp(
        new_last_paid,
        tz=timezone.utc,
    )

    await update_voice_session(
        guild_id,
        user_id,
        new_last_paid_at,
    )

    print(
        f"[ECONOMY][VOICE] "
        f"{user_id}: +{reward} "
        f"({complete_minutes} min)",
        flush=True,
    )


async def stop_voice_session(
    guild_id: int,
    user_id: int,
):
    session = await get_voice_session(
        guild_id,
        user_id,
    )

    if not session:
        return

    await process_voice_reward(
        guild_id,
        user_id,
        session[1],
    )

    await delete_voice_session(
        guild_id,
        user_id,
    )

    print(
        f"[ECONOMY][VOICE] "
        f"Usuario {user_id} salió de voz",
        flush=True,
    )


async def process_voice_sessions():
    if _client is None:
        return

    guild = _client.get_guild(GUILD_ID)

    if guild is None:
        return

    rows = await get_active_voice_sessions(
        GUILD_ID,
    )

    for user_id, last_paid_at in rows:

        member = guild.get_member(user_id)

        if (
            member is None
            or not user_counts_for_voice(member)
        ):
            await stop_voice_session(
                GUILD_ID,
                user_id,
            )
            continue

        await process_voice_reward(
            GUILD_ID,
            user_id,
            last_paid_at,
        )


async def voice_activity_loop():
    print(
        "[ECONOMY][VOICE] "
        "Sistema de actividad iniciado",
        flush=True,
    )

    await asyncio.sleep(10)

    while True:
        try:
            await process_voice_sessions()

        except asyncio.CancelledError:
            print(
                "[ECONOMY][VOICE] "
                "Sistema detenido",
                flush=True,
            )
            raise

        except Exception as error:
            print(
                "[ECONOMY][VOICE] "
                f"Error: {error}",
                flush=True,
            )

        await asyncio.sleep(
            max(
                10,
                VOICE_ACTIVITY_INTERVAL,
            )
        )


async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState,
):
    if member.guild.id != GUILD_ID:
        return

    if member.bot:
        return

    was_in_voice = before.channel is not None
    is_in_voice = after.channel is not None

    # Sale de voz
    if was_in_voice and not is_in_voice:
        await stop_voice_session(
            member.guild.id,
            member.id,
        )
        return

    # Cambio de canal
    if (
        was_in_voice
        and is_in_voice
        and before.channel.id != after.channel.id
    ):
        await stop_voice_session(
            member.guild.id,
            member.id,
        )

        if user_counts_for_voice(member):
            await start_voice_session(
                member.guild.id,
                member.id,
            )

        return

    # Entrada en voz
    if not was_in_voice and is_in_voice:
        if user_counts_for_voice(member):
            await start_voice_session(
                member.guild.id,
                member.id,
            )

        return

    # Cambio de mute/deaf/condición
    if is_in_voice:

        valid_before = (
            before.channel is not None
            and user_counts_for_voice(member)
        )

        valid_after = user_counts_for_voice(
            member
        )

        if not valid_before and valid_after:
            await start_voice_session(
                member.guild.id,
                member.id,
            )

        elif valid_before and not valid_after:
            await stop_voice_session(
                member.guild.id,
                member.id,
            )


async def on_ready():
    global _voice_task

    guild = _client.get_guild(GUILD_ID)

    if guild is not None:

        for channel in guild.voice_channels:

            for member in channel.members:

                if member.bot:
                    continue

                if not user_counts_for_voice(member):
                    continue

                existing = await get_voice_session(
                    GUILD_ID,
                    member.id,
                )

                if existing:
                    current = now()

                    await update_voice_session(
                        GUILD_ID,
                        member.id,
                        current,
                    )

                else:
                    await start_voice_session(
                        GUILD_ID,
                        member.id,
                    )

    if _voice_task is None:
        _voice_task = asyncio.create_task(
            voice_activity_loop()
        )