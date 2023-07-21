import telegram
from telegram import Update, InputMedia
from telegram.ext import ContextTypes

from ticket_bot import config
from ticket_bot.handlers.keyboards import get_my_tickets_keyboard
from ticket_bot.handlers.response import send_text_response, send_photo_response
from ticket_bot.services.ticket_service import get_user_tickets_db
from ticket_bot.templates.strings import Strings as s
from ticket_bot.templates.templates import render_template


async def show_my_tickets_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_tickets = await get_user_tickets_db(update.effective_user.id)
    if len(user_tickets) == 0:
        await send_text_response(update, context, response=s.NO_TICKETS_HERE)
        return
    ticket = user_tickets[0]
    if len(user_tickets) == 1:
        await send_photo_response(update, context,
                                  response=render_template("ticket.j2", {"t": ticket}),
                                  photo=ticket.qr_id)
    else:
        await send_photo_response(update, context,
                                  response=render_template("ticket.j2", {"t": ticket}),
                                  photo=ticket.qr_id,
                                  keyboard=get_my_tickets_keyboard(
                                      current_ticket_index=0,
                                      tickets_count=len(user_tickets),
                                      callback_prefix=config.SELECT_TICKET_CALLBACK_PATTERN
                                  ))


async def all_my_tickets_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    user_tickets = await get_user_tickets_db(update.effective_user.id)
    current_ticket_index = _get_current_ticket_index(query.data)
    ticket = user_tickets[current_ticket_index]
    await query.edit_message_media(media=InputMedia('photo', ticket.qr_id,
                                                    caption=render_template("ticket.j2", {"t": ticket}),
                                                    parse_mode=telegram.constants.ParseMode.HTML),
                                   reply_markup=get_my_tickets_keyboard(
                                       current_ticket_index=current_ticket_index,
                                       tickets_count=len(user_tickets),
                                       callback_prefix=config.SELECT_TICKET_CALLBACK_PATTERN,
                                   ))


def _get_current_ticket_index(query_data) -> int:
    pattern_prefix_length = len(config.SELECT_TICKET_CALLBACK_PATTERN)
    return int(query_data[pattern_prefix_length:])
