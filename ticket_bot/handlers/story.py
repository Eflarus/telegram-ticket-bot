import datetime as dt

from telegram import Update
from telegram.ext import ContextTypes

from ticket_bot.handlers.response import send_text_response
from ticket_bot.services.ticket_service import get_user_tickets_db
from ticket_bot.templates.templates import render_template


async def story_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_tickets = await get_user_tickets_db(update.effective_user.id, with_expired=True)
    expired = dt.datetime.now()
    await send_text_response(update, context,
                             response=render_template("story.j2",
                                                      {"ts": user_tickets, "start": 0, "expired": expired}))
