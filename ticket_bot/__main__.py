import logging

import pytz as pytz
from telegram.constants import ParseMode

from ticket_bot import config, handlers

from telegram.ext import (
    CommandHandler,
    ApplicationBuilder, PreCheckoutQueryHandler, MessageHandler, filters, CallbackQueryHandler, Defaults,
)

from ticket_bot.db import close_db
from ticket_bot.handlers import precheckout_handler, successful_payment_handler, error_handler, check_qr_handler
from ticket_bot.services.admin_service import get_admin_ids

COMMAND_HANDLERS = {
    "start": handlers.start,
    "help": handlers.help_,
    "events": handlers.get_event,
    "mytickets": handlers.show_my_tickets_handler,
    "story": handlers.story_handler,
    "stat": handlers.show_ticket_stat_handler,
}

CALLBACK_QUERY_HANDLERS = {
    rf"^{config.ALL_EVENTS_CALLBACK_PATTERN}(\d+)$": handlers.all_events_button,
    rf"^{config.SELECT_EVENT_CALLBACK_PATTERN}(\d+)$": handlers.events_with_tickets_button,
    rf"^{config.SELECT_TICKET_TYPE_CALLBACK_PATTERN}(\d+)$": handlers.get_ticket,
    rf"^{config.SELECT_TICKET_CALLBACK_PATTERN}(\d+)$": handlers.all_my_tickets_button,
}

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

if not config.TELEGRAM_BOT_TOKEN or not config.PAYMENT_PROVIDER_TOKEN:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN and PAYMENT_PROVIDER_TOKEN env variables "
        "wasn't implemented in .env (both should be initialized)."
    )


def main() -> None:
    """Run the bot."""
    defaults = Defaults(parse_mode=ParseMode.HTML, tzinfo=pytz.timezone('Europe/Moscow'))
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).defaults(defaults).build()

    for command_name, command_handler in COMMAND_HANDLERS.items():
        application.add_handler(CommandHandler(command_name, command_handler))

    for pattern, handler in CALLBACK_QUERY_HANDLERS.items():
        application.add_handler(CallbackQueryHandler(handler, pattern=pattern))

    # payment handlers
    application.add_handler(PreCheckoutQueryHandler(precheckout_handler))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))

    application.add_handler(MessageHandler(filters.PHOTO & filters.Chat(config.ADMIN_IDS), check_qr_handler))

    # error handler
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        logger.warning(traceback.format_exc())
    finally:
        close_db()
