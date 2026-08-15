import logging
from pyrogram import Client
from motor.motor_asyncio import AsyncIOMotorClient
import config

logging.basicConfig(level=logging.INFO)

class QuizBot(Client):
    def __init__(self):
        super().__init__(
            "QuizBotSession",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins=dict(root="plugins")
        )
        self.db = AsyncIOMotorClient(config.MONGO_URI)["QuizBotDB"]

    async def start(self):
        await super().start()
        print("🚀 Premium Quiz Bot Started Successfully!")

    async def stop(self, *args):
        await super().stop()
        print("🛑 Bot Stopped.")

if __name__ == "__main__":
    app = QuizBot()
    app.run()
  
