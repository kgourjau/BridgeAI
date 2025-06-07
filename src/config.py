import os
from dotenv import load_dotenv

# By using override=True, variables from the .env file will take precedence
# over system environment variables.
load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TARGET_API_KEY = os.getenv("TARGET_API_KEY")
TARGET_API_BASE_URL = os.getenv("TARGET_API_BASE_URL") 