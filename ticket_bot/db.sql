create table bot_user (
  telegram_id bigint primary key,
  username str default NULL,
  name str default NULL,
  last_name str default NULL,
  role int not null default 0,
  created_at timestamp default current_timestamp not null
);

create table event (
  id integer primary key,
  name varchar(124) not null,
  desc string default NULL,
  loc varchar(255) default NULL,
  date date not null,
  poster_id string default NULL,
  poster_file_name string not null,
  created_at timestamp default current_timestamp not null
);

create table ticket_type (
  id integer primary key,
  event_id int,
  quantity integer not null,
  price integer not null,
  desc varchar(255) not null,
  created_at timestamp default current_timestamp not null,
  foreign key(event_id) references event(id)
);

create table ticket (
  id integer primary key,
  ticket_type_id int not null,
  bot_user_id bigint not null,
  code varchar(255) not null unique,
  qr_id varchar(255) default NULL,
  payment_id varchar(255) not null unique,
  tg_payment_id varchar(255) not null unique,
  amount integer not null,
  email varchar(255),
  valid bool not null default true,
  deactivated_at timestamp default NULL,
  created_at timestamp default current_timestamp not null,
  foreign key(ticket_type_id) references ticket_type(id),
  foreign key(bot_user_id) references bot_user(telegram_id)
);

CREATE VIEW ticket_type_view AS
SELECT tt.id,
    CASE
        WHEN (SELECT COUNT(*)
              FROM ticket t
              JOIN ticket_type tt on tt.id = t.ticket_type_id
              WHERE t.ticket_type_id = tt.id AND t.valid = 1) <= tt.quantity-1 AND e.date > date('now') THEN 1
        ELSE 0
    END AS is_sold_less_valid_tickets
FROM ticket_type tt
JOIN event e on e.id = tt.event_id;