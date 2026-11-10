import json
import logging
import requests
from llm.conversation_context_db import get_user_threads

logger = logging.getLogger(__name__)

class TransparentThreadRouter:
    def __init__(self, api_url: str):
        self.api_url = f"{api_url}/v1/chat/completions"

    def determine_thread(self, user_id: int, user_message: str) -> str:
        existing_threads = get_user_threads(user_id)
        
        if not existing_threads:
            existing_threads = []

        # Cambiamos el prompt radicalmente: ya NO pedimos un JSON. 
        # Pedimos directamente la palabra o el nombre del tema en texto plano.
        prompt = (
            "Determina el tema o hilo de conversación para el mensaje del usuario.\n\n"
            f"Hilos activos del usuario: {existing_threads}\n"
            f"Mensaje del usuario: \"{user_message}\"\n\n"
            "REGLAS ESTRICTAS:\n"
            "1. Si el mensaje encaja con un hilo de la lista, responde ÚNICAMENTE con ese nombre exacto.\n"
            "2. Si es un tema nuevo, inventa un nombre de 1 o 2 palabras (ej: Mascotas, Tareas, Programación, Finanzas).\n"
            "3. Responde SOLO con el nombre del tema. No escribas introducciones, ni explicaciones, ni comillas, ni JSON."
        )

        try:
            payload = {
                "model": "default",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,  # Máxima precisión y consistencia
                "max_tokens": 20     # Forzamos una respuesta ultra corta
            }
            
            response = requests.post(self.api_url, json=payload, timeout=20) 
            
            if response.status_code == 200:
                # Obtenemos la respuesta de texto plano de llama-server
                chosen_thread = response.json()["choices"][0]["message"]["content"].strip()
                
                # Limpieza básica por si el modelo devuelve puntos finales, comillas o texto largo
                chosen_thread = chosen_thread.replace('"', '').replace("'", "").replace(".", "")
                chosen_thread = chosen_thread.strip()
                
                # Si el modelo se desvía y escribe demasiado, truncamos o caemos en General
                if len(chosen_thread) > 30 or not chosen_thread:
                    logger.warning(f"Respuesta del router demasiado larga o vacía: {chosen_thread}. Usando 'General'.")
                    return "General"
                    
                logger.info(f"Hilo asignado con éxito (Texto Plano): '{chosen_thread}'")
                return chosen_thread
                
        except Exception as e:
            logger.error(f"Error en la enrutación automática de temas: {e}", exc_info=True)
        
        return "General"

