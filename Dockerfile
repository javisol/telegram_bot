FROM python:3.10-slim

run mkdir -p /telegram_bot/calendar /telegram_bot/speech /telegram_bot/system /telegram_bot/weather

COPY all_requirements.txt /telegram_bot
COPY requirements.txt /telegram_bot
COPY bot.py /telegram_bot
COPY calendar/. /telegram_bot/calendar
COPY speech/. /telegram_bot/speech
COPY system/. /telegram_bot/system
COPY weather/. /telegram_bot/weather

WORKDIR /telegram_bot
RUN pip3 install -r all_requirements.txt

CMD ["python3", "bot.py"]