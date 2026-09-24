from decimal import Decimal

from .config import CURRENCY_SYMBOL


def format_money(amount):

    amount = Decimal(str(amount))

    return (
        f"{CURRENCY_SYMBOL} "
        f"{amount:,.2f}"
    )


def is_admin(interaction):

    return (
        interaction.guild is not None
        and interaction.user.guild_permissions.administrator
    )