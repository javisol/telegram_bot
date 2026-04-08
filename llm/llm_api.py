"""
LLM API integration module.
Forwards queries to the LLM API configured via environment variable.
"""
import os
import requests
import logging

logger = logging.getLogger(__name__)

# LLM API configuration - retrieved from environment variable
LLM_API_URL = os.environ.get("LLM_API_URL", "http://192.168.0.221:11444")


def query_llm(prompt: str) -> str:
    """
    Send a query to the LLM API and return the response.
    
    Args:
        prompt: The user's query to send to the LLM
        
    Returns:
        The LLM's response as a string
        
    Raises:
        requests.RequestException: If the API call fails
    """
    try:
        logger.info(f"Sending query to LLM API: {prompt[:50]}...")
        
        # System prompt to identify the AI
        system_prompt = "You are RatoncIA, an intelligent AI assistant. Provide helpful, accurate, and friendly responses."
        
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
                "max_tokens": 2048
            },
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Extract and return the response
        llm_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        logger.info(f"Received response from LLM API")
        return llm_response
        
    except requests.RequestException as e:
        logger.error(f"Error communicating with LLM API: {e}")
        raise


def query_llm_streaming(prompt: str) -> str:
    """
    Send a query to the LLM API with streaming support.
    
    Args:
        prompt: The user's query to send to the LLM
        
    Returns:
        The complete LLM response as a string
    """
    try:
        logger.info(f"Sending streaming query to LLM API: {prompt[:50]}...")
        
        # System prompt to identify the AI
        system_prompt = "You are RatoncIA, an intelligent AI assistant. Provide helpful, accurate, and friendly responses."
        
        response = requests.post(
            f"{LLM_API_URL}/v1/chat/completions",
            json={
                "model": "default",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "stream": True,
                "temperature": 0.7,
                "max_tokens": 2048
            },
            timeout=30
        )
        
        response.raise_for_status()
        
        # Collect streaming response
        full_response = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if decoded_line.startswith("data: "):
                    data = decoded_line[6:]
                    if data.startswith("[DONE]"):
                        break
                    try:
                        chunk = data[1:-1]  # Remove outer brackets
                        result = eval(chunk)
                        content = result.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        full_response += content
                    except Exception as e:
                        logger.warning(f"Error parsing streaming chunk: {e}")
        
        logger.info(f"Received streaming response from LLM API")
        return full_response
        
    except requests.RequestException as e:
        logger.error(f"Error communicating with LLM API: {e}")
        raise
