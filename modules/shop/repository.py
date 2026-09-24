from .database import db


async def get_shop_items(guild_id):

    return await db.fetchall(
        """
        SELECT
            id,
            name,
            description,
            price,
            stock,
            role_id

        FROM shop_items

        WHERE guild_id = %s

        ORDER BY price ASC, name ASC
        """,
        (guild_id,)
    )


async def get_shop_item(
    guild_id,
    name
):

    return await db.fetchone(
        """
        SELECT
            id,
            name,
            description,
            price,
            stock,
            role_id

        FROM shop_items

        WHERE guild_id = %s

        AND LOWER(name) = LOWER(%s)
        """,
        (
            guild_id,
            name
        )
    )


async def create_shop_item(
    guild_id,
    name,
    description,
    price,
    stock,
    role_id
):

    await db.execute(
        """
        INSERT INTO shop_items (

            guild_id,
            name,
            description,
            price,
            stock,
            role_id

        )

        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            guild_id,
            name,
            description,
            price,
            stock,
            role_id
        )
    )


async def delete_shop_item(
    guild_id,
    item_id
):

    await db.execute(
        """
        DELETE FROM shop_items

        WHERE id = %s

        AND guild_id = %s
        """,
        (
            item_id,
            guild_id
        )
    )


async def update_shop_item(
    guild_id,
    item_id,
    updates,
    values
):

    values = [
        *values,
        item_id,
        guild_id
    ]

    query = f"""
        UPDATE shop_items

        SET {", ".join(updates)}

        WHERE id = %s

        AND guild_id = %s
    """

    await db.execute(
        query,
        values
    )


async def get_inventory(
    guild_id,
    user_id
):

    return await db.fetchall(
        """
        SELECT
            s.name,
            s.description,
            i.quantity

        FROM inventory i

        INNER JOIN shop_items s
            ON s.id = i.item_id

        WHERE i.guild_id = %s

        AND i.user_id = %s

        AND i.quantity > 0

        ORDER BY s.name ASC
        """,
        (
            guild_id,
            user_id
        )
    )


async def get_item_count(guild_id):

    return await db.fetchone(
        """
        SELECT COUNT(*)

        FROM shop_items

        WHERE guild_id = %s
        """,
        (guild_id,)
    )