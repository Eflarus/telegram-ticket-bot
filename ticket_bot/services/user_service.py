import logging

from telegram import User

from ticket_bot.db import execute, fetch_one


async def insert_user_db(user: User | None) -> None:
    result = await execute(
        "INSERT OR IGNORE INTO bot_user (telegram_id, username, name, last_name) "
        "VALUES (:telegram_id, :username, :name, :last_name)",
        {"telegram_id": user.id, "username": user.username, "name": user.first_name, "last_name": user.last_name}),

    if result is not None:
        logging.info(f"new user: {user.id}")


async def set_user_role_db(telegram_user_id: int, role: int) -> None:
    result = await execute(
        "UPDATE bot_user SET role=:role WHERE telegram_id=:telegram_id",
        {"role": role, "telegram_id": telegram_user_id},
    )
    if result.rowcount > 0:
        logging.info(f"role for {telegram_user_id} updated to {role}")


async def get_user_db(user: User | None) -> bool:
    result = await fetch_one(
        "SELECT * FROM bot_user WHERE telegram_id = :telegram_id",
        {"telegram_id": user.id},
    )
    print(user)
    if result is None:
        await insert_user_db(user)
    return True
