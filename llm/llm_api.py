"""
LLM API integration module.
Forwards queries to the LLM API configured via environment variable.
"""
import os
import requests
import logging

logger = logging.getLogger(__name__)

# LLM API configuration - retrieved from environment variable
# Default to HTTPS for external services, HTTP for internal Docker network
LLM_API_URL = os.environ.get("LLM_API_URL", "http://rtn:11444")
TIMEOUT=300


def query_llm(prompt: str, stream: bool = False) -> str:
    """
    Send a query to the LLM API and return the response.
    
    Args:
        prompt: The user's query to send to the LLM
        stream: If True, use streaming response (default: False)
        
    Returns:
        The LLM's response as a string
        
    Raises:
        requests.RequestException: If the API call fails
    """
    try:
        # Sanitize prompt for logging to prevent sensitive data exposure
        sanitized_prompt = prompt[:50].replace(" ", "_").replace(":", "_").replace("\n", "_").replace("\t", "_")
        logger.info(f"Sending {'streaming ' if stream else ''}query to LLM API: {sanitized_prompt}...")
        
        # System prompt to identify the AI - configurable via environment variable
        system_prompt = os.environ.get("SYSTEM_PROMPT",
                                       "You are RatoncIA, an intelligent AI assistant. Provide helpful, accurate, and friendly responses. Answer in the language of the user's query.")
        
        # Warn if using HTTP for external services
        if not LLM_API_URL.startswith("https://") and not LLM_API_URL.startswith("http://rtn:"):
            logger.warning(f"LLM API using HTTP: {LLM_API_URL}")
        
        # Make POST request to the LLM API
        response = requests.post(
            f"{LLM_API_URL}/v1/chat/completions",
            json={
                "model": "default",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
                "stream": stream
            },
            timeout=TIMEOUT
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Extract and return the response
        llm_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        # Sanitize response for logging
        sanitized_response = llm_response[:50].replace(" ", "_").replace(":", "_")
        logger.info(f"Received {'streaming ' if stream else ''}response from LLM API: {sanitized_response}...")
        return llm_response
        
    except requests.RequestException as e:
        logger.error(f"Error communicating with LLM API: {e}")
        return "AI LLM is off"
