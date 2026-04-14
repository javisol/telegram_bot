FROM python:3.10-slim

# Create directories for application modules
RUN mkdir -p /telegram_bot/calendar /telegram_bot/speech /telegram_bot/system /telegram_bot/weather

# Copy application files
COPY all_requirements.txt /telegram_bot/
COPY requirements.txt /telegram_bot/
COPY bot.py /telegram_bot/
COPY calendar/. /telegram_bot/calendar/
COPY speech/. /telegram_bot/speech/
COPY system/. /telegram_bot/system/
COPY weather/. /telegram_bot/weather/

WORKDIR /telegram_bot

# Install dependencies
RUN pip3 install --no-cache-dir -r all_requirements.txt

# Create non-root user for security
RUN useradd -m -s /bin/bash telegrambot && \
    chown -R telegrambot:telegrambot /telegram_bot

# Set environment variables for runtime (can be overridden at runtime)
ENV TOKEN=${TOKEN} \
    LLM_API_URL=${LLM_API_URL:-https://llm-api.example.com:11444} \
    CAL_URL=${CAL_URL} \
    CAL_USER=${CAL_USER} \
    CAL_PASS=${CAL_PASS} \
    OBLIQUE_STRATEGIES_FILE=${OBLIQUE_STRATEGIES_FILE:-/data/repositories/telegram_bot/oblique_strategies/oblique_strategies_2015.json} \
    SYSTEM_PROMPT=${SYSTEM_PROMPT:-"You are RatoncIA, an intelligent AI assistant. Provide helpful, accurate, and friendly responses. Answer in the language of the user's query."}

# Switch to non-root user
USER telegrambot

# Add health check for container orchestration
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

CMD ["python3", "bot.py"]