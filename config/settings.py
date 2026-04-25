import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file at the project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Cohere API Configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_MODEL = os.getenv("COHERE_MODEL", "command")

if not COHERE_API_KEY or COHERE_API_KEY == "your_cohere_api_key_here":
    print("Warning: COHERE_API_KEY is not set correctly in the .env file.")
