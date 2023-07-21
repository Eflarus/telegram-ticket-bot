from io import BytesIO
from typing import cast

import telegram
from telegram import Chat, InlineKeyboardMarkup, Update, Message
from telegram.ext import ContextTypes


async def send_text_response(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        response: str,
        keyboard: InlineKeyboardMarkup | None = None,
) -> Message:
    args = {
        "chat_id": _get_chat_id(update),
        "disable_web_page_preview": True,
        "text": response,
        "parse_mode": telegram.constants.ParseMode.HTML,
    }
    if keyboard:
        args["reply_markup"] = keyboard

    message = await context.bot.send_message(**args)
    return message


async def send_photo_response(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        response: str,
        photo: str | BytesIO,
        keyboard: InlineKeyboardMarkup | None = None,
) -> Message:
    args = {
        "chat_id": _get_chat_id(update),
        "photo": photo,
        "caption": response,
        "parse_mode": telegram.constants.ParseMode.HTML,
    }
    if keyboard:
        args["reply_markup"] = keyboard

    message = await context.bot.send_photo(**args)
    return message


def _get_chat_id(update: Update) -> int:
    return cast(Chat, update.effective_chat).id
