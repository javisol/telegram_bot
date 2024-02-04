import os
import logging
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from weather import weather
from system import system_commands


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context.

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user

    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    text="Comandos: Ayuda"
    await update.message.reply_text(text)

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /weather is issued."""
    text=weather.get_weather_report()
    await update.message.reply_text(text)

async def uptime_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /uptime is issued."""
    text=system_commands.uptime()
    await update.message.reply_text(text)

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /ip is issued."""
    text=system_commands.ip()
    await update.message.reply_text(text)

async def fortune_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /fortune is issued."""
    text=system_commands.fortune()
    await update.message.reply_text(text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


def main() -> None:
    # Create the Application and pass it your bot's token.
    TOKEN = os.environ.get("TOKEN")
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    #system
    application.add_handler(CommandHandler("uptime", uptime_command))
    application.add_handler(CommandHandler("ip", ip_command))
    application.add_handler(CommandHandler("fortune", fortune_command))
    #weather
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(CommandHandler("tiempo", weather_command))
    #help
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ayuda", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()