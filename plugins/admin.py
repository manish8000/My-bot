from pyrogram import Client, filters
from pyrogram.types import Message
import config

@Client.on_message(filters.command("broadcast") & filters.user(config.ADMIN_ID))
async def broadcast_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/broadcast आपका मैसेज`")
        
    broadcast_msg = message.text.split(None, 1)[1]
    users = client.db["users"].find({})
    
    count = 0
    async for user in users:
        try:
            await client.send_message(user["user_id"], f"📣 **Announcement:**\n\n{broadcast_msg}")
            count += 1
        except Exception:
            pass
            
    await message.reply_text(f"✅ Broadcast Sent to {count} users!")
  
