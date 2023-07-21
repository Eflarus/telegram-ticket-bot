import logging
from typing import cast

import telegram
from telegram import Chat, Update, LabeledPrice
from telegram.ext import ContextTypes

from ticket_bot import config


async def send_prepared_invoice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    title: str,
    description: str,
    payload: str,
    product_label: str,
    price: int,
    photo_url: str | None = None,
) -> None:
    if config.IS_YOOCASSA:
        # Prepare receipt
        provider_data = {
            "receipt": {
                "items": [
                    {
                        "description": product_label,
                        "quantity": "1.00",
                        "amount": {
                            "value": f"{price}.00",
                            "currency": config.CURRENCY
                        },
                        "vat_code": 1,
                    }
                ]}
        }
        logging.info(f"prepared invoice for {update.effective_user.id}")

        args = {
            "chat_id": _get_chat_id(update),
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": config.PAYMENT_PROVIDER_TOKEN,
            "currency": config.CURRENCY,
            "prices": [LabeledPrice(product_label, price * 100)],
            "need_email": True,
            "send_email_to_provider": True,
            "provider_data": provider_data,
            "photo_url": photo_url,
        }
    else:
        args = {
            "chat_id": _get_chat_id(update),
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": config.PAYMENT_PROVIDER_TOKEN,
            "currency": config.CURRENCY,
            "prices": [LabeledPrice(product_label, price * 100)],
            "photo_url": photo_url,
        }

    await context.bot.send_invoice(**args)


def _get_chat_id(update: Update) -> int:
    return cast(Chat, update.effective_chat).id
