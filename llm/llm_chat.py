import os
import logging
from telegram import Update
from telegram.ext import ContextTypes

from llm.llm_api import query_llm
from llm.conversation_context import ConversationContextManager
from llm.image_processor import ImageProcessor
from llm.thread_router import TransparentThreadRouter
from llm.conversation_context_db import get_user_threads

logger = logging.getLogger(__name__)

LLM_API_URL = os.environ.get("LLM_API_URL", "http://rtn:11444")
router = TransparentThreadRouter(api_url=LLM_API_URL)

async def _process_input_and_run(update: Update, message_text: str, is_pure_image: bool = False) -> None:
    user_id = update.effective_user.id
    
    # 1. Determinar Hilo dinámicamente
    if not message_text.strip():
        active_thread = "General" if not is_pure_image else "Análisis Visual"
    else:
        # El router analiza el texto para decidir el hilo de forma transparente
        active_thread = router.determine_thread(user_id, message_text)
        
    # 2. Gestionar Archivos Multimedia (Imágenes)
    photo_file = None
    images = None
    if update.message and update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        
    if photo_file:
        image_processor = ImageProcessor()
        image_data = await image_processor.process_image(photo_file)
        if "error" not in image_data:
            images = [{
                "mime_type": image_data["mime_type"],
                "base64": image_data["base64"]
            }]
            logger.info(f"Imagen lista en memoria buffer para el hilo: {active_thread}")

    # 3. Cargar el contexto del hilo seleccionado
    context_manager = ConversationContextManager(user_id, thread_id=active_thread)
    context_history = context_manager.get_or_create()
    
    # 4. Notificar discretamente si se inicializa un contexto temático nuevo
    if active_thread != "General" and active_thread != "Análisis Visual" and len(context_history) == 0:
        await update.message.reply_text(f"📝 *Abriendo contexto:* _{active_thread}_", parse_mode="Markdown")

    # Guardar entrada en base de datos local
    history_save_text = message_text if message_text.strip() else "[Imagen]"
    context_manager.append("user", history_save_text)
    
    # 5. Ejecución del LLM a través de llm_api
    llm_response = query_llm(message_text, context=context_history, images=images)
    
    # Guardar respuesta del asistente en el hilo correspondiente
    context_manager.append("assistant", llm_response)
    
    # Enviar al chat de Telegram
    await update.message.reply_text(llm_response, parse_mode="HTML")

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        message_text = update.message.text or update.message.caption or ""
    else:
        message_text = ""
    await _process_input_and_run(update, message_text, is_pure_image=False)

async def ai_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _process_input_and_run(update, "", is_pure_image=True)

async def ai_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    try:
        # Se borra la totalidad de los hilos de este usuario
        context_manager = ConversationContextManager(user_id)
        context_manager.clear(clear_all=True)
        await update.message.reply_text("Historial completo (todos los hilos) borrado correctamente.", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error al limpiar base de datos: {e}")
        await update.message.reply_text("Hubo un error al borrar el historial.", parse_mode="HTML")


async def ai_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
<b>Comandos de IA (RatoncIA):</b>
/ai - Conversar de forma natural. Los hilos temáticos se organizan automáticamente de manera invisible.
/ai_image - Analizar una imagen de forma aislada.
/ai_clear - Eliminar todo el historial y limpiar todos los hilos creados.
/hilos - ver los temas que recuerda la IA (RatoncIA)
/ai_help - Ver esta ayuda.
"""
    await update.message.reply_text(help_text, parse_mode="HTML")


async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ai_chat(update, context)

async def ai_threads(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Muestra al usuario un listado con todos los hilos/temas de conversación 
    que la IA recuerda actualmente sobre él.
    """
    user_id = update.effective_user.id
    
    try:
        # Recuperamos la lista de hilos únicos del usuario
        existing_threads = get_user_threads(user_id)
        
        if not existing_threads:
            text = "🧠 *RatoncIA no tiene hilos temáticos activos para ti todavía.*\n\nTodas tus conversaciones actuales están guardadas bajo el contexto general."
            await update.message.reply_text(text, parse_mode="Markdown")
            return
            
        # Construimos un listado limpio usando viñetas emoji
        text_lines = ["🧠 *Temas que recuerdo sobre nuestras conversaciones:*", "--------------"]
        for thread in sorted(existing_threads):
            text_lines.append(f"• _{thread}_")
            
        text_lines.append("\n_Los hilos se gestionan automáticamente según el tema de tus mensajes._")
        
        await update.message.reply_text("\n".join(text_lines), parse_mode="Markdown")
        logger.info(f"Listado de hilos enviado al usuario {user_id}")
        
    except Exception as e:
        logger.error(f"Error al listar hilos para el usuario {user_id}: {e}")
        await update.message.reply_text(
            "Hubo un error al recuperar tus hilos de conversación.",
            parse_mode="HTML"
        )
