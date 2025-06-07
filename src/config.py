import os
from dotenv import load_dotenv

# By using override=True, variables from the .env file will take precedence
# over system environment variables.
load_dotenv(override=True)

# Generate a secret key with: python -c 'import secrets; print(secrets.token_hex(16))'
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-for-development")

# Token for web UI access
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# OpenAI/Target API Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TARGET_API_KEY = os.getenv("TARGET_API_KEY")
TARGET_API_BASE_URL = os.getenv("TARGET_API_BASE_URL")

# Bearer token for securing API endpoints
BEARER_TOKEN = os.getenv("BEARER")