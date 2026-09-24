import os

from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL no está definido"
    )


GUILD_ID = int(
    os.getenv("GUILD_ID", "0")
)

if GUILD_ID == 0:
    raise RuntimeError(
        "GUILD_ID no está definido"
    )


CURRENCY_NAME = os.getenv(
    "CURRENCY_NAME",
    "Coins"
)

CURRENCY_SYMBOL = os.getenv(
    "CURRENCY_SYMBOL",
    "💰"
)