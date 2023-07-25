import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN", "")
SUPPORT_TG = os.getenv("SUPPORT_TG", "")

BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB_FILE = BASE_DIR / "db.sqlite3"
TEMPLATES_DIR = BASE_DIR / "templates"

# In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
CURRENCY = "RUB"

IS_YOOCASSA = True

ADMIN_IDS = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS").split(",")]
DEVELOPER_CHAT_ID = ADMIN_IDS[0]
NOTIFY_ADMIN_ON_ERROR = False
DATE_FORMAT = "%d.%m.%Y"

ALL_EVENTS_CALLBACK_PATTERN = "events_"
SELECT_EVENT_CALLBACK_PATTERN = "event_"
SELECT_TICKET_TYPE_CALLBACK_PATTERN = "ticket_type_"
SELECT_TICKET_CALLBACK_PATTERN = "ticket_"

EVENT_START = "events"

LOG_FILE_NAME = "logs/bot.log"
TZ = "Europe/Moscow"
