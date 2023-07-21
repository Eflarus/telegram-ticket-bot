import asyncio
import datetime as dt
import logging
from typing import List

from ticket_bot.db import execute, fetch_one, fetch_all
from ticket_bot.models import Event


async def add_event_db(name: str,
                       desc: str | None,
                       loc: str | None,
                       date: dt.datetime,
                       poster_path: str | None,
                       ) -> bool:
    query = "INSERT INTO event (name, desc, loc, date, poster_file_name) " \
            "VALUES (:name, :desc, :loc, :date, :poster_file_name)"

    result = await execute(query, {"name": name, "desc": desc, "loc": loc, "date": date, "poster_file_name": poster_path})
    return result.rowcount > 0


async def get_last_event_db() -> Event | None:
    query = "SELECT * FROM event ORDER BY id DESC LIMIT 1"
    result = await fetch_one(query)
    if result:
        event = Event(*result.values())
        event.date = dt.datetime.strptime(event.date, '%Y-%m-%d %H:%M:%S.%f')
        return event
    else:
        logging.error("Couldn't get event'")
        return None


async def get_all_events_db() -> List[Event] | None:
    yesterday = dt.date.today() - dt.timedelta(days=1)
    query = "SELECT * FROM event WHERE date > DATE(:yesterday)"
    result = await fetch_all(query, {"yesterday": yesterday})
    if result:
        events = []
        for event in result:
            event = Event(*event.values())
            event.date = dt.datetime.strptime(event.date, '%Y-%m-%d %H:%M:%S.%f')
            events.append(event)
        return events
    else:
        logging.error("No events")
        return None


async def get_event_db(event_id: int) -> Event | None:
    query = "SELECT * FROM event WHERE id = :event_id"
    result = await fetch_one(query, {"event_id": event_id})
    if result:
        event = Event(*result.values())
        event.date = dt.datetime.strptime(event.date, '%Y-%m-%d %H:%M:%S.%f')
        return event
    else:
        logging.error("Couldn't find event'")
        return None


async def update_event_poster_id_db(event_id: int, poster_id: str) -> bool:
    query = "UPDATE event SET poster_id = :poster_id WHERE id = :id"
    result = await execute(query, {"poster_id": poster_id, "id": event_id})
    return result.rowcount > 0


if __name__ == "__main__":
    asyncio.run(add_event_db("Test Event Name",
                       "Short Description",
                       "Moscow, Pravda Club",
                       dt.datetime.now(),
                       "2.jpg"))
    asyncio.run(add_event_db("2",
                       "Short Description",
                       "Moscow, Pravda Club",
                       dt.datetime.now() - dt.timedelta(days=1),
                       "3.jpg"))
    asyncio.run(add_event_db("3",
                       "Short Description",
                       "Moscow, Pravda Club",
                       dt.datetime.now() + dt.timedelta(days=3),
                       "1.jpg"))

    print(asyncio.run(get_all_events_db()))


