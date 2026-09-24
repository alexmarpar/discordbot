from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from .config import CURRENCY_SYMBOL


def now():
    return datetime.now(timezone.utc)


def parse_time(value):
    if not value:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc,
            )

        return value

    try:
        return datetime.fromisoformat(str(value))
    except Exception:
        return None


def decimal_value(value):
    try:
        return Decimal(str(value))
    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return Decimal("0")


def money_decimal(value):
    return decimal_value(value).quantize(
        Decimal("0.01"),
    )


def format_money(amount):
    amount = decimal_value(amount)

    return (
        f"{CURRENCY_SYMBOL} "
        f"{amount:,.2f}"
    )


def format_duration(seconds):
    seconds = max(0, int(seconds))

    days, seconds = divmod(
        seconds,
        86400,
    )

    hours, seconds = divmod(
        seconds,
        3600,
    )

    minutes, seconds = divmod(
        seconds,
        60,
    )

    parts = []

    if days:
        parts.append(f"{days}d")

    if hours:
        parts.append(f"{hours}h")

    if minutes:
        parts.append(f"{minutes}m")

    if seconds or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)