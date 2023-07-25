import datetime
from dataclasses import dataclass


@dataclass
class Event:
    id: int
    name: str | None
    desc: str | None
    loc: str | None
    date: datetime.datetime
    poster_id: str | None
    poster_file_name: str | None
    created_at: datetime.datetime


@dataclass
class TicketType:
    id: int
    event_id: int
    quantity: int
    price: int
    desc: str
    created_at: datetime.datetime
    is_sold_less_valid_tickets: bool = None


@dataclass
class Ticket:
    id: int
    ticket_type_id: int
    user_id: int
    code: str
    qr_id: str | None
    payment_id: str
    tg_payment_id: str
    amount: float
    email: str | None
    valid: bool
    deactivated_at: datetime.datetime | None
    created_at: datetime.datetime
    last_check_at: datetime.datetime | None = None
    ticket_type_desc: str | None = None
    ticket_type_price: int | None = None
    event_id: int | None = None
    event_name: str | None = None
    event_desc: str | None = None
    event_date: datetime.datetime | None = None
    event_loc: str | None = None
    username: str | None = None


@dataclass
class TicketStat:
    id: int
    desc: str
    event_id: int
    event_name: str
    quantity: int
    price: int
    is_sold_less_valid_tickets: bool
    sold_valid_tickets: int
    sold_invalid_tickets: int


@dataclass
class TicketCheck:
    id: int
    code: str
    ticket_type_id: int
    ticket_type_desc: str
    amount: int
    email: str | None
    valid: bool
    deactivated_at: datetime.datetime | None
    created_at: datetime.datetime
    last_check_at: datetime.datetime | None
    event_name: str
    event_date: datetime.datetime
    user_id: int
    username: str | None
    name: str | None
    last_name: str | None
