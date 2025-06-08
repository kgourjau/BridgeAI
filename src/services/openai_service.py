import os
import requests
from src.config import (
    OPENAI_API_KEY,
    TARGET_API_KEY,
    TARGET_API_BASE_URL,
)


def openai_list_models():
    """Get OpenAI models list"""
    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def openai_chat_completion():
    """Make OpenAI chat completion request"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    messages = [
        {"role": "system", "content": "You are a test assistant."},
        {"role": "user", "content": "Testing. Just say hi and nothing else."},
    ]
    data = {"messages": messages, "model": "gpt-4o-mini"}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def openai_chat_completion_for_chat(messages: list):
    """
    Make chat completion request to the target API and format the response to resemble OpenAI's.
    """
    url = f"{TARGET_API_BASE_URL}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TARGET_API_KEY}",
    }
    data = {"messages": messages, "model": "llama-3.3-70b-versatile"}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    # Get the original response from the target API
    original_response = response.json()

    # Create a new, formatted response that mimics the OpenAI structure
    formatted_response = {
        "id": original_response.get("id"),
        "object": "chat.completion",
        "created": original_response.get("created"),
        "model": original_response.get("model"),
        "choices": original_response.get("choices"),
        "system_fingerprint": original_response.get("system_fingerprint")
    }

    # Re-format the usage object to match OpenAI's standard
    if "usage" in original_response and original_response["usage"]:
        original_usage = original_response["usage"]
        formatted_response["usage"] = {
            "prompt_tokens": original_usage.get("prompt_tokens"),
            "completion_tokens": original_usage.get("completion_tokens"),
            "total_tokens": original_usage.get("total_tokens")
        }
    else:
        formatted_response["usage"] = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        
    return formatted_response 


def openai_chat_completion_stream():
    """Make OpenAI chat completion streaming request"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    messages = [
        {"role": "system", "content": "You are a test assistant."},
        {"role": "user", "content": "Testing. Just say hi and nothing else."},
    ]
    data = {"messages": messages, "model": "gpt-4o-mini", "stream": True}
    response = requests.post(url, headers=headers, json=data, stream=True)
    response.raise_for_status()
    return response.iter_lines()


def openai_chat_completion_for_chat_stream(payload: dict):
    """
    Make a streaming chat completion request to the target API.
    Returns the raw response object for manual stream handling.
    """
    url = f"{TARGET_API_BASE_URL}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TARGET_API_KEY}",
    }

    payload["stream"] = True
    if "model" not in payload:
        payload["model"] = "llama-3.3-70b-versatile"

    # url = "https://api.openai.com/v1/chat/completions"
    # headers = {
    #     "Content-Type": "application/json",
    #     "Authorization": f"Bearer {OPENAI_API_KEY}",
    # }
    # payload["model"] = "gpt-4o-mini"



    response = requests.post(url, headers=headers, json=payload, stream=True)
    response.raise_for_status()
    return response 