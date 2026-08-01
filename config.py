import os
from dotenv import load_dotenv

load_dotenv()

HARDCOVER_API_KEY = os.getenv("HARDCOVER_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
