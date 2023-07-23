from dataclasses import dataclass


@dataclass
class Strings:
    BUY_TICKET = "Купить билет"
    ERROR_SORRY = "Внезапная ошибка ("
    BACK_TO_MENU = "Вернуться"
    NO_TICKETS_HERE = "Билетов нет"
    INVOICE_TITLE = "Билет"
    ERROR_POST_PAYMENT = "Что-то пошло не так, свяжитесь с администратором!"
    SOLDOUT = "Все билеты проданы, купить не получится"
    NO_QR_IN_PHOTO = "Билет на фото не обнаружен"
    FAKE_TICKET_CODE = "Билета с таким номером в базе нет"
