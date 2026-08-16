import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client
from motor.motor_asyncio import AsyncIOMotorClient
import config

# ---------------- 1. Health Check Web Server for Koyeb / Render ---------------- #
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

# वेब सर्वर को बैकग्राउंड थ्रेड में स्टार्ट करें
threading.Thread(target=run_health_check_server, daemon=True).start()

# ---------------- 2. Pyrogram Bot Client Setup ---------------- #
plugins = dict(root="plugins")

app = Client(
    "my_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=plugins
)

# ---------------- 3. Run Bot ---------------- #
if __name__ == "__main__":
    print("🤖 Bot is starting and loading plugins...")
    app.run()
    
