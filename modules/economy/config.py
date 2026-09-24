import os
from decimal import Decimal, InvalidOperation

from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not defined")


GUILD_ID = int(os.getenv("GUILD_ID", "0"))

if GUILD_ID == 0:
    raise RuntimeError("GUILD_ID is not defined")


CURRENCY = os.getenv(
    "CURRENCY_NAME",
    "Coins",
)

CURRENCY_SYMBOL = os.getenv(
    "CURRENCY_SYMBOL",
    "💰",
)


try:
    STARTING_BALANCE = Decimal(
        os.getenv("STARTING_BALANCE", "0"),
    )
except InvalidOperation:
    STARTING_BALANCE = Decimal("0")


try:
    VOICE_REWARD_PER_MINUTE = Decimal(
        os.getenv(
            "VOICE_REWARD_PER_MINUTE",
            "0.02",
        ),
    )
except InvalidOperation:
    VOICE_REWARD_PER_MINUTE = Decimal("0.02")


VOICE_ACTIVITY_INTERVAL = int(
    os.getenv(
        "VOICE_ACTIVITY_INTERVAL",
        "60",
    ),
)


VOICE_REQUIRE_OTHERS = (
    os.getenv(
        "VOICE_REQUIRE_OTHERS",
        "false",
    ).lower()
    in ("1", "true", "yes", "on")
)


VOICE_IGNORE_AFK = (
    os.getenv(
        "VOICE_IGNORE_AFK",
        "true",
    ).lower()
    in ("1", "true", "yes", "on")
)