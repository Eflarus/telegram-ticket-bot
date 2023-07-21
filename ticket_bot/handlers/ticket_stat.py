from telegram import Update
from telegram.ext import ContextTypes

from ticket_bot.handlers.response import send_text_response
from ticket_bot.services.admin_service import for_admin
from ticket_bot.services.ticket_type_service import get_tickets_stat_db
from ticket_bot.templates.strings import Strings as s
from ticket_bot.templates.templates import render_template


@for_admin
async def show_ticket_stat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    stat = await get_tickets_stat_db()
    if len(stat) == 0:
        await send_text_response(update, context, response=s.NO_TICKETS_HERE)
        return

    await send_text_response(update, context, response=render_template("ticket_stat.j2", {"s": stat}))
