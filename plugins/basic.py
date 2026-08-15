from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    user = message.from_user
    db = client.db["users"]
    await db.update_one({"user_id": user.id}, {"$set": {"name": user.full_name}}, upsert=True)
    
    await message.reply_text(
        f"🪐 **Hello {user.first_name}!**\n\n"
        "Welcome to **Premium Quiz Bot** 🚀\n"
        "सभी फीचर्स और कमांड्स देखने के लिए `/help` भेजें।"
    )

@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    text = (
        "🧭 **Premium Quiz Bot Commands:**\n\n"
        "📌 **Basic:**\n"
        "• `/start` - Check Alive Status 🪐\n"
        "• `/help` - Help & Command List 🧭\n"
        "• `/stats` - View Your Stats 📊\n"
        "• `/features` - Explore Features 🎟️\n\n"
        "📝 **Quiz Management:**\n"
        "• `/create` - Build a New Quiz 🛠️\n"
        "• `/quiz` - Launch a Quiz 🚀\n"
        "• `/quizid` - Start Quiz by ID 🧩\n"
        "• `/myquizzes` - View Your Quizzes 🗂️\n\n"
        "📄 **PDF & TXT Import:**\n"
        "• `/pdfimport` - Import Questions from PDF 📁\n"
        "• `/txtimport` - Import Questions from TXT 📄\n\n"
        "⏱️ **Control:**\n"
        "• `/stop` - Stop Quiz Immediately 🛑\n"
        "• `/pause` - Pause Quiz Temporarily ⏸️\n"
        "• `/resume` - Resume Quiz ▶️"
    )
    await message.reply_text(text, parse_mode="markdown")

@Client.on_message(filters.command("features"))
async def features_cmd(client: Client, message: Message):
    await message.reply_text(
        "🎟️ **Premium Bot Features:**\n"
        "1. Instant PDF/TXT to Quiz Converter\n"
        "2. Custom Timer & Negative Marking\n"
        "3. Live Leaderboard & HTML Report Generation\n"
        "4. Auto-Scrape Polls from Public Channels\n"
        "5. Group Moderation (Mute/Ban/Welcome)"
    )
  
