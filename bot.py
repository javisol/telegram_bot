"""
Telegram bot for system administration and weather updates.
Handles commands for system monitoring, weather, LLM queries, and more.
"""
import os
import logging
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from weather import weather
from system import system_commands
from speech import speech_recog
from llm import llm_api
from llm.conversation_context import ConversationContextManager
from llm.llm_chat import ai_chat, ai_image, ai_clear, ai_help, ai_command, ai_threads


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# =============================================================================
# Command Handlers
# =============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    text = """
<b>Comandos:</b>
--------------
Ayuda
Uptime
fwflush
unban
fail2ban        - Controlar fail2ban (start/stop)
Ip
geoip
Cita
Tiempo
Habla
Remind          - Configurar recordatorio
Oblique (ob)
AI              - Chatear con la IA (RatoncIA)
ai_image        - Analizar una imagen
ai_clear        - Borrar historial de conversación
ai_help         - Ayuda sobre comandos de IA
hilos           - ver los temas que recuerda la IA (RatoncIA)
"""
    await update.message.reply_text(text, parse_mode="HTML")


# =============================================================================
# System Commands
# =============================================================================

async def uptime_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /uptime command."""
    text = system_commands.uptime()
    await update.message.reply_text(text)


async def fwflush_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /fwflush command."""
    text = system_commands.firewall_flush()
    await update.message.reply_text(text)


async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /unban command."""
    input_text = update.message.text
    text = system_commands.firewall_unban(input_text)
    await update.message.reply_text(text)


async def fail2ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /fail2ban command."""
    input_text = update.message.text
    text = system_commands.firewall_fail2ban(input_text)
    await update.message.reply_text(text)


async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /ip command."""
    text = system_commands.ip()
    await update.message.reply_text(text)


async def geoip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /geoip command."""
    input_text = update.message.text
    text = system_commands.geoip(input_text)
    await update.message.reply_text(text)


async def fortune_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /cita command."""
    text = system_commands.fortune()
    await update.message.reply_text(text)


# =============================================================================
# Weather Commands
# =============================================================================

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /weather command."""
    text = weather.get_weather_report()
    await update.message.reply_text(text)


# =============================================================================
# Speech Commands
# =============================================================================

async def talk_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /talk command."""
    text = update.message.text
    audio_file = system_commands.talk(text)


async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process voice messages sent by users."""
    file_path = "/tmp/voice_file.ogg"
    voice_note = await context.bot.get_file(update.message.voice.file_id)
    voice_file = await voice_note.download_to_drive(file_path)
    text = f"Procesando audio..."
    wav_file = system_commands.audio_to_wav(file_path)
    text = speech_recog.speech_to_text_from_file(wav_file)
    await update.message.reply_text(text)


# =============================================================================
# Reminder Commands
# =============================================================================

async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /remind command."""
    text = update.message.text
    response = system_commands.reminder(text)
    await update.message.reply_text(response)


# =============================================================================
# Oblique Strategy Commands
# =============================================================================

async def oblique_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /oblique command."""
    text = update.message.text
    response = system_commands.oblique()
    await update.message.reply_text(response)


# =============================================================================
# Echo Handler (for non-command text messages)
# =============================================================================

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle non-command text messages."""
    await update.message.reply_text(update.message.text)


# =============================================================================
# Bot Setup and Registration
# =============================================================================

def main() -> None:
    """Initialize and run the Telegram bot."""
    TOKEN = os.environ.get("TOKEN")
    
    # Se han ampliado los timeouts HTTP aquí para evitar fallos por latencia local del LLM
    application = (
        Application.builder()
        .token(TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .build()
    )
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ayuda", help_command))
    
    # System command handlers
    application.add_handler(CommandHandler("uptime", uptime_command))
    application.add_handler(CommandHandler("fwflush", fwflush_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("fail2ban", fail2ban_command))
    application.add_handler(CommandHandler("ip", ip_command))
    application.add_handler(CommandHandler("geoip", geoip_command))
    application.add_handler(CommandHandler("cita", fortune_command))
    application.add_handler(CommandHandler("fortune", fortune_command))
    
    # Weather command handlers
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(CommandHandler("tiempo", weather_command))
    
    # Speech command handlers
    application.add_handler(CommandHandler("habla", talk_command))
    application.add_handler(CommandHandler("talk", talk_command))
    
    # Reminder command handlers
    application.add_handler(CommandHandler("recuerda", remind_command))
    application.add_handler(CommandHandler("remind", remind_command))
    
    # Oblique strategy command handlers
    application.add_handler(CommandHandler("oblique", oblique_command))
    application.add_handler(CommandHandler("ob", oblique_command))
    
    # AI/LLM command handlers
    application.add_handler(CommandHandler("ai", ai_chat))
    application.add_handler(CommandHandler("ai_image", ai_image))
    application.add_handler(CommandHandler("ai_clear", ai_clear))
    application.add_handler(CommandHandler("ai_help", ai_help))
    application.add_handler(CommandHandler("hilos", ai_threads))
    
    # Message handlers
    application.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, ai_chat))
    
    # Voice messages - process and transcribe
    application.add_handler(MessageHandler(filters.VOICE, audio_command))
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

