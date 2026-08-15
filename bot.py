import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client
import config

# Koyeb Health Check पास करने के लिए छोटा Web Server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is Running Alive!")

    def log_message(self, format, *args):
        return  # Logs को साफ़ रखने के लिए HTTP लॉग्स छिपाएँ

def run_health_check_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Web Server को background thread में चालू करें
threading.Thread(target=run_health_check_server, daemon=True).start()

# Bot Setup
plugins = dict(root="plugins")

app = Client(
    "QuizBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=plugins
)

if __name__ == "__main__":
    print("🚀 Premium Quiz Bot Started Successfully!")
    app.run()
    
