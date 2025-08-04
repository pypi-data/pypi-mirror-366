import os

from dotenv import load_dotenv

load_dotenv()
# sets for the script, doesn't need to be passed in to anything
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
