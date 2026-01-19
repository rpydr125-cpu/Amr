import os

class Config:
    API_ID = int(os.environ.get("API_ID", "12345"))
    API_HASH = os.environ.get("API_HASH", "your_hash_here")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_token_here")
    # Aapki Akamai API
    API_URL = "https://hindibhaskarbyamarnathapi.akamai.net.in/xstream?url="
  
