#!/usr/bin/env python3
import os
import json
import requests
from dotenv import load_dotenv

from src.services.openai_service import openai_chat_completion_for_chat

# Load environment variables from .env
load_dotenv()


def list_models(api_key):
    """List available OpenAI models."""
    url = "https://api.openai.com/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def chat_completion(api_key, messages):
    """Get ChatGPT completion using the chat endpoint."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-3.5-turbo",  # Change model if needed.
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return
    
    # Demo: List models
    print("Fetching models from OpenAI...")
    try:
        models = list_models(api_key)
        print("Models:")
        print(json.dumps(models, indent=2))
    except Exception as e:
        print(f"Error listing models: {e}")

    # Demo: Chat completion using full messages list
    print("\nRequesting chat completion from OpenAI...")
    messages = [
        {"role": "system", "content": "You are ChatGPT, a large language model."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
    try:
        result = chat_completion(api_key, messages)
        print("Chat Completion Response:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error in chat completion: {e}")

    # Demo: Chat completion for chat using single message API
    print("\nRequesting chat completion for chat using single message...")
    try:
        result_for_chat = openai_chat_completion_for_chat("Hi")
        print("Chat Completion for Chat Response:")
        print(json.dumps(result_for_chat, indent=2))
    except Exception as e:
        print(f"Error in chat completion for chat: {e}")


if __name__ == "__main__":
    main() 