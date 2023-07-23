from typing import List

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from ticket_bot.models import TicketType
from ticket_bot.templates.strings import Strings as s


def get_events_keyboard(current_event_index: int,
                        events_count: int,
                        callback_prefix: str,
                        callback_select_prefix: str,
                        ) -> InlineKeyboardMarkup:
    prev_index = current_event_index - 1
    if prev_index < 0:
        prev_index = events_count - 1
    next_index = current_event_index + 1
    if next_index > events_count - 1:
        next_index = 0
    keyboard = [
        [
            InlineKeyboardButton("<", callback_data=f"{callback_prefix}{prev_index}"),
            InlineKeyboardButton(
                f"{s.BUY_TICKET}", callback_data=f"{callback_select_prefix}{current_event_index}"
            ),
            InlineKeyboardButton(
                ">",
                callback_data=f"{callback_prefix}{next_index}",
            ),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_single_event_keyboard(ticket_types: List[TicketType],
                              callback_ticket_prefix: str,
                              ) -> InlineKeyboardMarkup:
    keyboard = []
    if ticket_types is not None:
        keyboard += [
            [InlineKeyboardButton(f"{ticket_t.desc} ({ticket_t.price} р)",
                                  callback_data=f"{callback_ticket_prefix}{ticket_t.id}")] for ticket_t in ticket_types
        ]
    return InlineKeyboardMarkup(keyboard)


def get_tickets_keyboard(current_event_index: int,
                         ticket_types: List[TicketType],
                         callback_ticket_prefix: str,
                         callback_event_prefix: str
                         ) -> InlineKeyboardMarkup:
    keyboard = []
    if ticket_types is not None:
        keyboard += [
            [InlineKeyboardButton(f"{ticket_t.desc} ({ticket_t.price} р)",
                                  callback_data=f"{callback_ticket_prefix}{ticket_t.id}")] for ticket_t in ticket_types if ticket_t.is_sold_less_valid_tickets
        ]
    keyboard.append(
        [InlineKeyboardButton(f"{s.BACK_TO_MENU}", callback_data=f"{callback_event_prefix}{current_event_index}")])
    return InlineKeyboardMarkup(keyboard)


def get_my_tickets_keyboard(current_ticket_index: int,
                            tickets_count: int,
                            callback_prefix: str
                            ) -> InlineKeyboardMarkup:
    prev_index = current_ticket_index - 1
    if prev_index < 0:
        prev_index = tickets_count - 1
    next_index = current_ticket_index + 1
    if next_index > tickets_count - 1:
        next_index = 0
    keyboard = [
        [
            InlineKeyboardButton("<", callback_data=f"{callback_prefix}{prev_index}"),
            InlineKeyboardButton(">", callback_data=f"{callback_prefix}{next_index}"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
