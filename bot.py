import os
import logging
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from weather import weather
from system import system_commands
from speech import speech_recog
from llm import llm_api


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
    """Handle the /start command.
    
    Sends a welcome message to the user when they start the bot.
    
    Args:
        update: Telegram update object containing user information
        context: Context object containing bot reference
    """
    user = update.effective_user

    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process voice messages sent by users.
    
    Downloads the voice file, converts it to WAV format, performs speech-to-text
    recognition, and sends the transcribed text back to the user.
    
    Args:
        update: Telegram update object containing voice message
        context: Context object containing bot reference
    """
    file_path = "/tmp/voice_file.ogg"
    voice_note = await context.bot.get_file(update.message.voice.file_id)
    voice_file = await voice_note.download_to_drive(file_path)
    text = f"Procesando audio..."
    wav_file = system_commands.audio_to_wav(file_path)
    text = speech_recog.speech_to_text_from_file(wav_file)
    await update.message.reply_text(text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command.
    
    Sends a list of available commands to the user.
    
    Args:
        update: Telegram update object
        context: Context object containing bot reference
    """
    text = "Comandos:\n--------------\nAyuda\nUptime\nfwflush\nunban\nfail2ban\nIp\ngeoip\nCita\nTiempo\nHabla\nRemind\nOblique (ob)\nAI\n"
    await update.message.reply_text(text)

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /weather command.
    
    Retrieves and sends the current weather report to the user.
    
    Args:
        update: Telegram update object
        context: Context object containing bot reference
    """
    text = weather.get_weather_report()
    await update.message.reply_text(text)

async def uptime_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /uptime command.
    
    Retrieves and sends the server uptime information to the user.
    
    Args:
        update: Telegram update object
        context: Context object containing bot reference
    """
    text = system_commands.uptime()
    await update.message.reply_text(text)

async def fwflush_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /fwflush command.
    
    Flushes firewall rules and sends the result to the user.
    
    Args:
        update: Telegram update object
        context: Context object containing bot reference
    """
    text = system_commands.firewall_flush()
    await update.message.reply_text(text)

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /unban command.
    
    Unbans a specific IP from fail2ban based on user input.
    
    Args:
        update: Telegram update object containing the IP address
        context: Context object containing bot reference
    """
    input_text = update.message.text
    text = system_commands.firewall_unban(input_text)
    await update.message.reply_text(text)

async def fail2ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /fail2ban command.
    
    Starts or stops the fail2ban service based on user input.
    
    Args:
        update: Telegram update object containing the action (start/stop)
        context: Context object containing bot reference
    """
    input_text = update.message.text
    text = system_commands.firewall_fail2ban(input_text)
    await update.message.reply_text(text)

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /ip command.
    
    Retrieves and sends the current IP address to the user.
    
    Args:
        update: Telegram update object
        context: Context object containing bot reference
    """
    text = system_commands.ip()
    await update.message.reply_text(text)

async def geoip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /geoip command.
    
    Performs a geoIP lookup for the specified IP address.
    
    Args:
        update: Telegram update object containing the IP address
        context: Context object containing bot reference
    """
    input_text = update.message.text
    text = system_commands.geoip(input_text)
    await update.message.reply_text(text)

async def fortune_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /cita command.
    
    Retrieves and sends a random fortune message to the user.
    
    Args:
        update: Telegram update object
        context: Context object containing bot reference
    """
    text = system_commands.fortune()
    await update.message.reply_text(text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle non-command text messages.
    
    Echoes the user's message back to them.
    
    Args:
        update: Telegram update object containing the message
        context: Context object containing bot reference
    """
    await update.message.reply_text(update.message.text)

async def talk_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /talk command.
    
    Sends a voice message response based on user input.
    
    Args:
        update: Telegram update object containing the message
        context: Context object containing bot reference
    """
    text = update.message.text
    audio_file = system_commands.talk(text)

async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /remind command.
    
    Sets a reminder for a specific time or duration based on user input.
    
    Args:
        update: Telegram update object containing time and message
        context: Context object containing bot reference
    """
    text = update.message.text
    response = system_commands.reminder(text)
    await update.message.reply_text(response)

async def oblique_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /oblique command.
    
    Retrieves and sends a random oblique strategy card.
    
    Args:
        update: Telegram update object
        context: Context object containing bot reference
    """
    text = update.message.text
    response = system_commands.oblique()
    await update.message.reply_text(response)


async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /ai command.
    
    Forwards the user's query to the LLM API and returns the AI's response.
    
    Args:
        update: Telegram update object containing the message
        context: Context object containing bot reference
    """
    prompt = update.message.text
    
    # Validate input length to prevent DoS
    MAX_PROMPT_LENGTH = 4096
    if len(prompt) > MAX_PROMPT_LENGTH:
        await update.message.reply_text(
            f"Prompt too long. Maximum length is {MAX_PROMPT_LENGTH} characters. "
            f"Your prompt was {len(prompt)} characters.",
            parse_mode="Markdown"
        )
        return
    
    # Sanitize prompt for logging
    sanitized_prompt = prompt[:50].replace(" ", "_").replace(":", "_").replace("\n", "_").replace("\t", "_")
    
    try:
        logger.info(f"Processing AI query: {sanitized_prompt}...")
        response = llm_api.query_llm(prompt)
        await update.message.reply_text(response)
    except Exception as e:
        error_msg = f"Error communicating with AI: {str(e)}"
        logger.error(error_msg)
        await update.message.reply_text(error_msg)


def main() -> None:
    # Create the Application and pass it your bot's token.
    TOKEN = os.environ.get("TOKEN")
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    #system
    application.add_handler(CommandHandler("uptime", uptime_command))
    application.add_handler(CommandHandler("fwflush", fwflush_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("fail2ban", fail2ban_command))
    application.add_handler(CommandHandler("ip", ip_command))
    application.add_handler(CommandHandler("geoip", geoip_command))
    application.add_handler(CommandHandler("cita", fortune_command))
    application.add_handler(CommandHandler("fortune", fortune_command))
    #weather
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(CommandHandler("tiempo", weather_command))
    application.add_handler(CommandHandler("habla", talk_command))
    application.add_handler(CommandHandler("talk", talk_command))
    application.add_handler(CommandHandler("recuerda", remind_command))
    application.add_handler(CommandHandler("remind", remind_command))
    application.add_handler(CommandHandler("oblique", oblique_command))
    application.add_handler(CommandHandler("ob", oblique_command))
    # AI
    application.add_handler(CommandHandler("ai", ai_command))
    #help
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ayuda", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # voice handler
    application.add_handler(MessageHandler(filters.VOICE, audio_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()