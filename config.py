import os

# Telegram API Credentials (my.telegram.org से मिलते हैं)
API_ID = int(os.environ.get("API_ID", "123456"))  
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")

# Bot Token & Mongo
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
MONGO_URI = os.environ.get("MONGO_URI", "YOUR_MONGO_URI")

# Admin Settings
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))

# Groq AI Settings
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
