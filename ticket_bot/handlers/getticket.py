from telegram import Update
from telegram.ext import ContextTypes

from ticket_bot import config
from ticket_bot.handlers.prepared_invoice import send_prepared_invoice
from ticket_bot.services.event_service import get_event_db
from ticket_bot.services.ticket_type_service import get_ticket_type_db
from ticket_bot.services.user_service import get_user_db
from ticket_bot.templates.templates import render_template
from ticket_bot.templates.strings import Strings as s


async def get_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends an invoice without shipping-payment."""
    await get_user_db(update.callback_query.from_user)
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    ticket_type_id = _get_selected_ticket_id(query.data)
    ticket_type = await get_ticket_type_db(ticket_type_id)
    event = await get_event_db(ticket_type.event_id)
    title = s.INVOICE_TITLE
    description = render_template("invoice.j2", {"event": event, "ticket_t": ticket_type})
    # select a payload just for you to recognize it's the donation from your bot
    payload = f"pay-{update.effective_user.id}-{ticket_type.id}"
    price = ticket_type.price
    product_label = ticket_type.desc
    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    await send_prepared_invoice(update, context, title, description, payload, product_label, price)


def _get_selected_ticket_id(query_data) -> int:
    pattern_prefix_length = len(config.SELECT_TICKET_TYPE_CALLBACK_PATTERN)
    return int(query_data[pattern_prefix_length:])
