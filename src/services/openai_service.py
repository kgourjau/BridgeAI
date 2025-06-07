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


def openai_chat_completion_for_chat(user_message: str):
    """Make chat completion request to the target API"""
    url = f"{TARGET_API_BASE_URL}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TARGET_API_KEY}",
    }
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_message},
    ]
    data = {"messages": messages, "model": "llama-3.3-70b-versatile"}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json() 