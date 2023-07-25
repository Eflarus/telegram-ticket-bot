import datetime as dt
import logging
import string
from typing import List

from ticket_bot.db import fetch_all, execute, fetch_one
from ticket_bot.models import Ticket, TicketCheck


async def add_ticket_db(ticket_type_id: int,
                        user_id: int,
                        payment_id: str,
                        tg_payment_id: str,
                        amount: float,
                        email: str | None) -> Ticket | None:
    code = f"t{user_id}-{payment_id}-{ticket_type_id}"
    query = "INSERT INTO ticket (ticket_type_id, bot_user_id, code, payment_id, tg_payment_id, amount, email) " \
            "VALUES (:ticket_type_id, :bot_user_id, :code, :payment_id, :tg_payment_id, :amount, :email)"

    result = await execute(query, {"ticket_type_id": ticket_type_id, "bot_user_id": user_id,
                                   "code": code, "payment_id": payment_id, "tg_payment_id": tg_payment_id,
                                   "amount": amount, "email": email})
    new_ticket = await fetch_one("SELECT * FROM ticket WHERE id = last_insert_rowid()")
    if new_ticket is not None:
        ticket = Ticket(*new_ticket.values())
        return ticket
    else:
        return None


async def get_user_tickets_db(user_id: int, with_expired: bool = False) -> List[Ticket] | None:
    yesterday = dt.datetime.now() - dt.timedelta(days=1)
    query = """SELECT s.*, tt.desc, tt.price, e.id AS event_id, e.name as event_name, 
                    e.desc as event_desc, e.date as event_date, e.loc as event_loc
                FROM ticket s
                JOIN ticket_type tt ON s.ticket_type_id = tt.id
                JOIN event e ON tt.event_id = e.id
                WHERE s.bot_user_id = :user_id"""
    if not with_expired:
        query += " AND e.date > DATETIME(:yesterday)"
    query += " ORDER BY e.date ASC"
    result = await fetch_all(query, {"user_id": user_id, "yesterday": yesterday})
    if result is not None:
        tickets = []
        for ticket in result:
            ticket = Ticket(*ticket.values())
            ticket.event_date = dt.datetime.strptime(ticket.event_date, '%Y-%m-%d %H:%M:%S.%f')
            ticket.created_at = dt.datetime.strptime(ticket.created_at, '%Y-%m-%d %H:%M:%S')
            tickets.append(ticket)
        return tickets
    else:
        return None


async def get_ticket_db(ticket_id: int) -> Ticket | None:
    query = """SELECT t.*,
                tt.desc, tt.price, e.id AS event_id, e.name as event_name, 
                    e.desc as event_desc, e.date as event_date, e.loc as event_loc, bu.username
                FROM ticket t
                JOIN ticket_type tt ON t.ticket_type_id = tt.id
                JOIN event e ON tt.event_id = e.id
                JOIN bot_user bu on bu.telegram_id = t.bot_user_id
                WHERE t.id = :ticket_id"""
    result = await fetch_one(query, {"ticket_id": ticket_id})
    if result is not None:
        ticket = Ticket(*result.values())
        ticket.event_date = dt.datetime.strptime(ticket.event_date, '%Y-%m-%d %H:%M:%S.%f')
        ticket.created_at = dt.datetime.strptime(ticket.created_at, '%Y-%m-%d %H:%M:%S')
        return ticket
    else:
        return None


async def add_ticket_qr_db(ticket_id: int, qr_id: str) -> bool:
    query = "UPDATE ticket SET qr_id = :qr_id WHERE id = :id"
    result = await execute(query, {"qr_id": qr_id, "id": ticket_id})
    return result.rowcount > 0


async def check_ticket_db(code: string) -> TicketCheck | None:
    query = """SELECT t.id, t.code, tt.id AS ticket_type_id, tt.desc AS ticket_type_desc, t.amount, 
                t.email, t.valid, t.deactivated_at, t.created_at, t.last_check_at,
                e.name AS event_name, e.date AS event_date,
                bu.telegram_id AS bot_user_id, bu.username, bu.name, bu.last_name  
                FROM ticket t
                JOIN ticket_type tt ON tt.id = t.ticket_type_id
                JOIN event e ON e.id = tt.event_id
                JOIN bot_user bu ON bu.telegram_id = t.bot_user_id
                WHERE code = :code"""
    result = await fetch_one(query, {"code": code})
    if result is not None:
        tc = TicketCheck(*result.values())
        tc.event_date = dt.datetime.strptime(tc.event_date, '%Y-%m-%d %H:%M:%S.%f')
        tc.created_at = dt.datetime.strptime(tc.created_at, '%Y-%m-%d %H:%M:%S')
        tc.deactivated_at = dt.datetime.strptime(tc.deactivated_at, '%Y-%m-%d %H:%M:%S') if tc.deactivated_at else None
        tc.last_check_at = dt.datetime.strptime(tc.last_check_at, '%Y-%m-%d %H:%M:%S') if tc.last_check_at else None
        await execute("UPDATE ticket SET last_check_at = current_timestamp WHERE id = :id", {"id": tc.id})
        return tc
    else:
        return None


if __name__ == "__main__":
    pass
