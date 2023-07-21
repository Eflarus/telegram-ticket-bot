import logging
from io import BytesIO

import qrcode
from telegram import Update
from telegram.ext import ContextTypes

from ticket_bot.handlers.response import send_text_response, send_photo_response
from ticket_bot.services.admin_service import notify_admins
from ticket_bot.services.ticket_service import add_ticket_db, add_ticket_qr_db, get_ticket_db
from ticket_bot.services.ticket_type_service import get_ticket_stat_db
from ticket_bot.templates.templates import render_template
from ticket_bot.templates.strings import Strings as s


# after (optional) shipping, it's the pre-checkout
async def precheckout_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    logging.info(f"PreCheckoutHandler for {update.effective_user.id}")
    ticket_type = int(update.pre_checkout_query.invoice_payload.split('-')[2])
    check = await get_ticket_stat_db(ticket_type)
    if not check.is_sold_less_valid_tickets:
        await query.answer(ok=False, error_message=s.SOLDOUT)
    # check the payload, is this from your bot?
    elif not query.invoice_payload.startswith(f"pay-{update.effective_user.id}"):
        # answer False pre_checkout_query
        await query.answer(ok=False, error_message=s.ERROR_POST_PAYMENT)
    else:
        await query.answer(ok=True)


# finally, after contacting the payment provider...
async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirms the successful payment."""
    payment = update.message.successful_payment
    ticket_type_id = _get_ticket_type_from_payload(update)
    logging.info(f"{payment.provider_payment_charge_id=}, {payment.order_info.email=}")

    ticket = await add_ticket_db(ticket_type_id=ticket_type_id,
                                 user_id=update.effective_user.id,
                                 payment_id=payment.provider_payment_charge_id,
                                 tg_payment_id=payment.telegram_payment_charge_id,
                                 amount=payment.total_amount,
                                 email=payment.order_info.email)
    if ticket is not None:
        t = await get_ticket_db(ticket.id)
        bytes_io = BytesIO()
        img = qrcode.make(ticket.code)
        img.save(bytes_io)
        bytes_io.seek(0)
        qr_msg = await send_photo_response(update, context,
                                           response=render_template("successful_payment.j2", {"t": t}),
                                           photo=bytes_io)
        photo_fileID = qr_msg.photo[-1].file_id
        await add_ticket_qr_db(ticket_id=ticket.id, qr_id=photo_fileID)
        await notify_admins(render_template("successful_payment_admin.j2", {"t": t}), context)
    else:
        await send_text_response(update, context, response=s.ERROR_POST_PAYMENT)


def _get_ticket_type_from_payload(update: Update) -> int:
    return int(update.message.successful_payment.invoice_payload.split('-')[2])
