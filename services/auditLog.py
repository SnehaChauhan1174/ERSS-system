import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import json
import re

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

