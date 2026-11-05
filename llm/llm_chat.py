"""
LLM Chat Handler for Telegram Bot.

This module provides a high-level interface for chatting with the LLM API
through the Telegram bot, with automatic conversation context management.
Supports multimodal input (text and images).
"""
import os
import logging
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes

from llm import llm_api
from llm.llm_api import query_llm
from llm.conversation_context import ConversationContextManager
from llm.image_processor import ImageProcessor, prepare_multimodal_content

logger = logging.getLogger(__name__)


async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle AI chat queries with conversation context.
    
    This command allows users to chat with the AI assistant, and the
    conversation history is automatically tracked and used for context
    in subsequent messages. Supports both text-only and multimodal (text + images) input.
    
    Args:
        update: Telegram update object containing user information
        context: Context object containing bot reference
    """
    user = update.effective_user
    user_id = user.id
    
    try:
        # Get or create conversation context for this user
        context_manager = ConversationContextManager(user_id)
        context_history = context_manager.get_or_create()
        
        # Lee tanto el texto normal como el texto adjunto a una foto
        if update.message:
            message_text = update.message.text or update.message.caption or ""
        else:
            message_text = ""
        
        # Check if there's an attached photo (Corregido con await)
        photo_file = None
        if update.message and update.message.photo:
            # Get the highest resolution photo
            photo_file = await update.message.photo[-1].get_file()
        
        # Process image if available
        images = None
        if photo_file:
            image_processor = ImageProcessor()
            image_data = await image_processor.process_image(photo_file)
            if "error" not in image_data:
                images = [
                    {
                        "mime_type": image_data["mime_type"],
                        "base64": image_data["base64"]
                    }
                ]
                logger.info(f"Image processed for user {user_id}: {image_data['file_name']}")
        
        # Check if message is empty (only image or no content)
        if not message_text.strip() and not images:
            await update.message.reply_text(
                "Por favor, escribe un mensaje para la IA.",
                parse_mode="HTML"
            )
            return
        
        # Guardar el mensaje del usuario en el historial antes de enviar la petición
        history_text = message_text if message_text else "[Imagen enviada]"
        context_manager.append("user", history_text)
        
        # Build conversation context with current message
        max_messages = context_manager.history_limit
        current_context = context_history[-max_messages:] if len(context_history) > max_messages else context_history
        
        # Query the LLM API
        logger.info(f"Processing AI query for user {user_id}: {message_text[:50] if message_text else 'Image'}...")
        
        # Pass images to the LLM API if available
        llm_response = query_llm(message_text, context=current_context, images=images)
        
        # Append assistant response to context
        context_manager.append("assistant", llm_response)
        
        # Send response to user (Usa HTML por seguridad ante caracteres conflictivos)
        await update.message.reply_text(
            llm_response,
            parse_mode="HTML"
        )
        
        logger.info(f"AI response sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in AI chat for user {user_id}: {e}")
        await update.message.reply_text(
            "Hubo un error al comunicarse con la IA. Intenta de nuevo más tarde.",
            parse_mode="HTML"
        )


async def ai_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle image messages specifically for image analysis.
    
    This command allows users to send images for analysis without additional text.
    
    Args:
        update: Telegram update object containing user information
        context: Context object containing bot reference
    """
    user = update.effective_user
    user_id = user.id
    
    try:
        # Get or create conversation context for this user
        context_manager = ConversationContextManager(user_id)
        context_history = context_manager.get_or_create()
        
        # Check if there's an attached photo (Corregido con await)
        photo_file = None
        if update.message and update.message.photo:
            # Get the highest resolution photo
            photo_file = await update.message.photo[-1].get_file()
        
        if not photo_file:
            await update.message.reply_text(
                "Por favor, envía una imagen para que la IA la analice.",
                parse_mode="HTML"
            )
            return
        
        # Process image
        image_processor = ImageProcessor()
        image_data = await image_processor.process_image(photo_file)
        
        if "error" in image_data:
            await update.message.reply_text(
                f"Error al procesar la imagen: {image_data['error']}",
                parse_mode="HTML"
            )
            return
        
        logger.info(f"Image processed for user {user_id}: {image_data['file_name']}")
        
        # Guardar en el historial
        context_manager.append("user", "[Imagen enviada para análisis]")
        
        # Build conversation context with current message
        max_messages = context_manager.history_limit
        current_context = context_history[-max_messages:] if len(context_history) > max_messages else context_history
        
        # Query LLM with just the image (no text prompt)
        llm_response = query_llm("", context=current_context, images=[
            {
                "mime_type": image_data["mime_type"],
                "base64": image_data["base64"]
            }
        ])
        
        # Append assistant response to context
        context_manager.append("assistant", llm_response)
        
        # Send response to user
        await update.message.reply_text(
            llm_response,
            parse_mode="HTML"
        )
        
        logger.info(f"AI response sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in AI image for user {user_id}: {e}")
        await update.message.reply_text(
            "Hubo un error al procesar la imagen. Intenta de nuevo más tarde.",
            parse_mode="HTML"
        )


async def ai_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Clear conversation history for a user.
    
    Args:
        update: Telegram update object
        context: Context object containing bot reference
    """
    user = update.effective_user
    user_id = user.id
    
    try:
        # Create context manager and clear history
        context_manager = ConversationContextManager(user_id)
        context_manager.clear()
        
        await update.message.reply_text(
            "Historial de conversación borrado. Puedes continuar chateando con la IA.",
            parse_mode="HTML"
        )
        logger.info(f"Cleared conversation history for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error clearing conversation history for user {user_id}: {e}")
        await update.message.reply_text(
            "Hubo un error al borrar el historial.",
            parse_mode="HTML"
        )


async def ai_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show AI command help information.
    
    Args:
        update: Telegram update object
        context: Context object containing bot reference
    """
    help_text = """
<b>Comandos de IA:</b>

/ai - Chatear con la IA (RatoncIA) - Texto o imagen
/ai_image - Analizar una imagen enviada
/ai_clear - Borrar historial de conversación
/ai_help - Mostrar esta ayuda
"""
    await update.message.reply_text(help_text, parse_mode="HTML")


async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /ai command or default behavior.
    
    Forwards the user's query to the LLM API with conversation context
    and returns the AI's response.
    """
    # Como tu handler principal ahora redirige todo a ai_chat de forma polimórfica,
    # simplemente hacemos que ai_command delegue el trabajo si recibe entradas complejas.
    await ai_chat(update, context)
