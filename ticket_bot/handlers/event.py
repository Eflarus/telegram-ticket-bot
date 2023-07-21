import telegram
from telegram import Update, InputMedia
from telegram.ext import ContextTypes

from ticket_bot import config
from ticket_bot.handlers.keyboards import get_events_keyboard, get_tickets_keyboard, get_single_event_keyboard
from ticket_bot.handlers.response import send_photo_response
from ticket_bot.models import Event
from ticket_bot.services.event_service import update_event_poster_id_db, get_all_events_db, get_event_db
from ticket_bot.services.ticket_type_service import get_ticket_types_for_event_db

from ticket_bot.templates.templates import render_template


async def get_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends an event info."""
    events = await get_all_events_db()
    event = events[0]
    if event.poster_id is None:
        await _upload_poster_to_telegram(event, context)
        event = await get_event_db(event.id)
    if len(events) == 1:
        ticket_types = await get_ticket_types_for_event_db(event.id)
        await send_photo_response(update, context,
                                  response=render_template("event.j2", {"event": event}),
                                  photo=event.poster_id,
                                  keyboard=get_single_event_keyboard(
                                      ticket_types=ticket_types,
                                      callback_ticket_prefix=config.SELECT_TICKET_TYPE_CALLBACK_PATTERN,
                                  ))
    else:
        await send_photo_response(update, context,
                                  response=render_template("event.j2", {"event": event}),
                                  photo=event.poster_id,
                                  keyboard=get_events_keyboard(
                                      current_event_index=0,
                                      events_count=len(events),
                                      callback_prefix=config.ALL_EVENTS_CALLBACK_PATTERN,
                                      callback_select_prefix=config.SELECT_EVENT_CALLBACK_PATTERN
                                  ))


async def all_events_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    events = await get_all_events_db()
    current_event_index = _get_current_event_index(query.data)
    event = events[current_event_index]
    if event.poster_id is None:
        await _upload_poster_to_telegram(event, context)
        event = await get_event_db(event.id)
    await query.edit_message_media(media=InputMedia('photo', event.poster_id,
                                                    caption=render_template("event.j2", {"event": event}),
                                                    parse_mode=telegram.constants.ParseMode.HTML),
                                   reply_markup=get_events_keyboard(
                                       current_event_index=current_event_index,
                                       events_count=len(events),
                                       callback_prefix=config.ALL_EVENTS_CALLBACK_PATTERN,
                                       callback_select_prefix=config.SELECT_EVENT_CALLBACK_PATTERN
                                   ))


async def events_with_tickets_button(update: Update, _: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    selected_event_index = _get_selected_event_index(query.data)
    event = await get_event_db(selected_event_index+1)
    ticket_types = await get_ticket_types_for_event_db(event.id)
    await query.edit_message_reply_markup(reply_markup=get_tickets_keyboard(
        current_event_index=event.id,
        ticket_types=ticket_types,
        callback_ticket_prefix=config.SELECT_TICKET_TYPE_CALLBACK_PATTERN,
        callback_event_prefix=config.ALL_EVENTS_CALLBACK_PATTERN
    ))


def _get_current_event_index(query_data) -> int:
    pattern_prefix_length = len(config.ALL_EVENTS_CALLBACK_PATTERN)
    return int(query_data[pattern_prefix_length:])


def _get_selected_event_index(query_data) -> int:
    pattern_prefix_length = len(config.SELECT_EVENT_CALLBACK_PATTERN)
    return int(query_data[pattern_prefix_length:])


async def _upload_poster_to_telegram(event: Event, context: ContextTypes.DEFAULT_TYPE):
    # sending the photo to discover its file_id:
    poster_path = "images/posters/" + event.poster_file_name
    print(poster_path)
    photo = await context.bot.send_photo(chat_id=config.DEVELOPER_CHAT_ID, photo=open(poster_path, 'rb'))
    photo_fileID = photo.photo[-1].file_id
    await update_event_poster_id_db(event.id, poster_id=photo_fileID)
