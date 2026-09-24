import os

from dotenv import load_dotenv


load_dotenv()


GUILD_ID = int(os.getenv("GUILD_ID", "0"))
DATABASE_URL = os.getenv("DATABASE_URL")


if GUILD_ID == 0:
    raise RuntimeError("GUILD_ID is not defined")


if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not defined")
