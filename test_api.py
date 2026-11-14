
import os
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Read the OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

# Check whether the key exists
if api_key and api_key != "your_actual_api_key_here":
    print("SUCCESS! OpenAI API key loaded.")
else:
    print("ERROR! API key not found.")
