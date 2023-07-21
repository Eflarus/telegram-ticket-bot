FROM python:3.11
WORKDIR /ticket-bot
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD python -m ticket_bot