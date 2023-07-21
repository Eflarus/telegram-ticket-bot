import asyncio
from typing import List

from ticket_bot.db import execute, fetch_one, fetch_all
from ticket_bot.models import TicketType, TicketStat


async def add_ticket_type_db(event_id: int, quantity: int, price: int, desc: str) -> bool:
    query = "INSERT INTO ticket_type (event_id, quantity, price, desc) VALUES (:event_id, :quantity, :price, :desc)"
    result = await execute(query, {"event_id": event_id, "quantity": quantity, "price": price, "desc": desc})
    return result.rowcount > 0


async def get_ticket_types_for_event_db(event_id: int) -> List[TicketType] | None:
    query = """SELECT tt.*, ttw.is_sold_less_valid_tickets
                FROM ticket_type tt 
                JOIN ticket_type_view ttw ON ttw.id = tt.id
                WHERE event_id = :event_id"""
    result = await fetch_all(query, {"event_id": event_id})
    if result:
        ticket_types = []
        for ticket_type in result:
            ticket_types.append(TicketType(*ticket_type.values()))
        return ticket_types
    else:
        return None


async def get_ticket_type_db(ticket_type_id: int) -> TicketType | None:
    query = """SELECT tt.*, ttw.is_sold_less_valid_tickets
                FROM ticket_type tt 
                JOIN ticket_type_view ttw ON ttw.id = tt.id 
                WHERE tt.id = :ticket_type_id"""
    result = await fetch_one(query, {"ticket_type_id": ticket_type_id})
    if result:
        ticket_type = TicketType(*result.values())
        return ticket_type
    else:
        return None


async def get_ticket_stat_db(ticket_type_id: int) -> TicketStat | None:
    query = """SELECT tt.id, tt.desc, tt.event_id, e.name as event_name, tt.quantity, tt.price, ttw.is_sold_less_valid_tickets,
                       (SELECT COUNT(*) FROM ticket t WHERE t.ticket_type_id = tt.id AND t.valid = true) AS sold_valid_tickets,
                       (SELECT COUNT(*) FROM ticket t WHERE t.ticket_type_id = tt.id AND t.valid = false) AS sold_invalid_tickets
                FROM ticket_type tt
                JOIN ticket_type_view ttw ON ttw.id = tt.id 
                JOIN event e on tt.event_id = e.id
                WHERE tt.id = :ticket_type_id
                GROUP BY tt.id;"""
    result = await fetch_one(query, {"ticket_type_id": ticket_type_id})
    if result:
        ticket_stat = TicketStat(*result.values())
        return ticket_stat
    else:
        return None


async def get_tickets_stat_db() -> List[TicketStat] | None:
    query = """SELECT tt.id, tt.desc, tt.event_id, e.name as event_name,tt.quantity, tt.price, ttw.is_sold_less_valid_tickets,
                       (SELECT COUNT(*) FROM ticket t WHERE t.ticket_type_id = tt.id AND t.valid = true) AS sold_valid_tickets,
                       (SELECT COUNT(*) FROM ticket t WHERE t.ticket_type_id = tt.id AND t.valid = false) AS sold_invalid_tickets
                FROM ticket_type tt
                JOIN ticket_type_view ttw ON ttw.id = tt.id 
                JOIN event e on tt.event_id = e.id
                GROUP BY tt.id;"""
    result = await fetch_all(query)
    if result:
        tickets_stat = []
        for ticket_type in result:
            tickets_stat.append(TicketStat(*ticket_type.values()))
        return tickets_stat
    else:
        return None


if __name__ == "__main__":
    # pass
    asyncio.run(add_ticket_type_db(2, 3, 100, "проходка"))
    asyncio.run(add_ticket_type_db(1, 2, 500, "VIP билет в правду"))
    asyncio.run(add_ticket_type_db(1, 2, 100, "стандарт билет в правду"))
    # print(asyncio.run(get_ticket_types_for_event_db(1)))
    # print(asyncio.run(get_ticket_type_by_id_db(1)))
