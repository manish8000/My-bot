import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client
from motor.motor_asyncio import AsyncIOMotorClient
import config

# Koyeb Health Check Web Server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is Running Alive!")

    def log_message(self, format, *args):
        return

def run_health_check_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# MongoDB Setup
mongo_client = AsyncIOMotorClient(
    config.MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True
)
db = mongo_client["QuizBotDB"]

# Bot Setup
plugins = dict(root="plugins")

app = Client(
    "QuizBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=plugins
)

app.db = db

if __name__ == "__main__":
    print("🚀 Premium Quiz Bot Started Successfully!")
    app.run()
    
