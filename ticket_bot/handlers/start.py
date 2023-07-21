import logging
from io import BytesIO

import qrcode
from telegram import Update
from telegram.ext import ContextTypes

from ticket_bot.handlers.response import send_text_response, send_photo_response
from ticket_bot.services.user_service import insert_user_db, get_user_db
from ticket_bot.templates.templates import render_template

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await get_user_db(update.message.from_user)
    await send_text_response(update, context, response=render_template("start.j2"))
