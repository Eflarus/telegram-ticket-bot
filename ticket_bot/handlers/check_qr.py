import logging
from io import BytesIO

import cv2
import numpy as np
from telegram import Update
from telegram.ext import ContextTypes

from ticket_bot.handlers.response import send_text_response
from ticket_bot.services.ticket_service import check_ticket_db
from ticket_bot.templates.strings import Strings as s
from ticket_bot.templates.templates import render_template


async def check_qr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo_qr = await update.effective_message.photo[-1].get_file()
    bytes_io = BytesIO()
    await photo_qr.download_to_memory(bytes_io)
    bytes_io.seek(0)
    file_bytes = np.asarray(bytearray(bytes_io.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    qcd = cv2.QRCodeDetector()
    retval, decoded_info, points, straight_qrcode = qcd.detectAndDecodeMulti(img)
    if retval:
        logging.info(decoded_info)
        tc = await check_ticket_db(decoded_info[0])
        if tc is not None:
            # logging.info(tc)
            await send_text_response(update, context, response=render_template("ticket_check.j2", {"tc": tc}))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=s.FAKE_TICKET_CODE)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=s.NO_QR_IN_PHOTO)
