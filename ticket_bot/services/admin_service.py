import logging
from typing import cast, List

import telegram
from telegram import Update, User
from telegram.ext import ContextTypes

from ticket_bot import config
from ticket_bot.db import fetch_one, fetch_all


async def is_admin(telegram_user_id: int) -> bool:
    result = await fetch_one(
        "SELECT role FROM bot_user WHERE telegram_id=:telegram_id",
        {"telegram_id": telegram_user_id},
    )
    if result:
        role = result.get("role")
        return role == 1
    return False


async def get_admin_ids() -> List[int]:
    results = await fetch_all(
        "SELECT telegram_id FROM bot_user WHERE role=1"
    )
    admin_ids = [result.get("telegram_id") for result in results]
    return admin_ids


def for_admin(handler):
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = cast(User, update.effective_user).id
        if user_id not in config.ADMIN_IDS:
            return
        await handler(update, context)

    return wrapped


async def notify_admins(text_notification: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    for admin_id in config.ADMIN_IDS:
        try:
            args = {
                "chat_id": admin_id,
                "disable_web_page_preview": True,
                "text": text_notification,
                "parse_mode": telegram.constants.ParseMode.HTML,
            }

            await context.bot.send_message(**args)
        except Exception as e:
            logging.info(f"Exception while notify admin{admin_id} ")
