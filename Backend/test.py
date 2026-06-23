import os
from google import genai
from pathlib import Path
from dotenv import load_dotenv

# The client automatically picks up the GEMINI_API_KEY environment variable
try:
    # Find the .env file in the parent (root) folder
    root_dir = Path(__file__).resolve().parent.parent
    env_path = root_dir / '.env'

    # Explicitly load it into system environment variables
    load_dotenv(dotenv_path=env_path)
    client = genai.Client()

    print(" Testing free-tier connection with gemini-2.5-flash...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello! Confirming connection.",
    )

    print("\n API Response Success:")
    print(response.text)

except Exception as e:
    print(f"\n Setup Error: {e}")
    print("Please double-check your environment variables.")