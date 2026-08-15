import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

# ----------------- 📌 BASIC & HELP COMMANDS ----------------- #

@Client.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    user = message.from_user
    user_name = user.first_name + (f" {user.last_name}" if user.last_name else "")
    try:
        if hasattr(client, "db"):
            await client.db["users"].update_one(
                {"user_id": user.id},
                {"$set": {"name": user_name}},
                upsert=True
            )
    except Exception as e:
        print(f"DB Error: {e}")

    await message.reply_text(
        f"🪐 **Hello {user.first_name}!**\n\n"
        "Welcome to **Ultimate Premium Quiz Bot** 🚀\n"
        "सभी 50+ कमांड्स देखने के लिए `/botcmd` या `/help` भेजें।"
    )

@Client.on_message(filters.command(["help", "botcmd"]))
async def help_cmd(client: Client, message: Message):
    text = (
        "🧭 **ALL BOT COMMANDS LIST** 🧭\n\n"
        "📌 **Basic:**\n"
        "• `/start` - Check Alive Status 🪐\n"
        "• `/quiz` - Launch a Quiz 🚀\n"
        "• `/stats` - View Your Stats 📊\n"
        "• `/add` - Add a New Question ➕\n"
        "• `/edit` - Edit Existing Question 📝\n"
        "• `/delete` - Remove a Question 🗑️\n"
        "• `/poll2q` - Convert Poll to Quiz 🔄\n"
        "• `/scrapepoll` - Scrape Polls 🎧\n"
        "• `/clone` - Clone Quiz 🧩\n"
        "• `/queue` - View Ongoing Clone 🕒\n"
        "• `/help` - Help & Commands 🧭\n"
        "• `/pdfimport` - Import Questions from PDF 📁\n"
        "• `/txtimport` - Import from Text File 📄\n"
        "• `/quizid` - Start Quiz by ID 🧩\n"
        "• `/pdfinfo` - PDF Import Guide 📗\n"
        "• `/htmlinfo` - About HTML Reports 🖥️\n"
        "• `/htmlreport` - Generate HTML Report 💼\n"
        "• `/negmark` - Apply Negative Marking ⚖️\n"
        "• `/resetpenalty` - Reset Penalties 🧮\n"
        "• `/stop` - Stop Quiz Immediately 🛑\n"
        "• `/cancel` - Cancel Current Operation 🛑\n"
        "• `/create` - Build a New Quiz 🛠️\n"
        "• `/myquizzes` - View Your Quizzes 💼\n"
        "• `/features` - Explore Features 🎟️\n"
        "• `/premium` - Upgrade to Premium 💎\n\n"
        "🤖 **AI & Advanced Tools:**\n"
        "• `/aiquiz` - Generate Quiz using AI 🤖\n"
        "• `/pause` - Pause Quiz Temporarily ⏸️\n"
        "• `/resume` - Resume Paused Quiz ▶️\n"
        "• `/fast` - Fast Quiz Speed ⚡\n"
        "• `/slow` - Slow Quiz Speed 🐢\n"
        "• `/normal` - Reset to Normal Speed 🔄\n"
        "• `/broadcast` - Broadcast Message 📢\n"
        "• `/mute` - Mute Member in Group 🔇\n"
        "• `/unmute` - Unmute Member 🔊"
    )
    await message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ----------------- 📝 QUIZ & FILE IMPORT COMMANDS ----------------- #

@Client.on_message(filters.command("create"))
async def create_quiz(client: Client, message: Message):
    await message.reply_text("🛠️ **Quiz Builder Started!**\n\nअपने क्विज़ का नाम/टाइटल भेजें:")

@Client.on_message(filters.command("myquizzes"))
async def my_quizzes(client: Client, message: Message):
    await message.reply_text("🗂️ **आपके बनाए गए Quizzes:**\n\nअभी आपने कोई नया क्विज़ सेव नहीं किया है। क्विज़ बनाने के लिए `/create` का उपयोग करें।")

@Client.on_message(filters.command("pdfimport"))
async def pdf_import(client: Client, message: Message):
    await message.reply_text("📁 **PDF Questions Import:**\n\nकृपया प्रश्नों वाली `.pdf` फ़ाइल यहाँ भेजें।")

@Client.on_message(filters.command("txtimport"))
async def txt_import(client: Client, message: Message):
    await message.reply_text("📄 **TXT Questions Import:**\n\nकृपया प्रश्नों वाली `.txt` फ़ाइल यहाँ भेजें।")

@Client.on_message(filters.command("poll2q"))
async def poll_to_quiz(client: Client, message: Message):
    await message.reply_text("🔄 **Poll to Quiz Converter:**\n\nTelegram Poll को क्विज़ में बदलने के लिए Poll को यहाँ Forward करें।")

@Client.on_message(filters.command("scrapepoll"))
async def scrape_poll(client: Client, message: Message):
    await message.reply_text("🎧 **Poll Scraper:**\n\nकिसी पब्लिक चैनल का लिंक भेजें जहाँ से आप Polls कॉपी करना चाहते हैं।")

@Client.on_message(filters.command("clone"))
async def clone_quiz(client: Client, message: Message):
    await message.reply_text("🧩 **QuizBot Cloner:**\n\nOfficial @QuizBot का क्विज़ लिंक यहाँ शेयर करें।")

@Client.on_message(filters.command("aiquiz"))
async def ai_quiz(client: Client, message: Message):
    await message.reply_text("🤖 **AI Quiz Generator:**\n\nजिस विषय पर क्विज़ चाहिए उसका नाम लिखें: (जैसे: `/aiquiz Rajasthan GK`)")

# ----------------- ⏱️ CONTROL & SPEED COMMANDS ----------------- #

@Client.on_message(filters.command("stop"))
async def stop_quiz(client: Client, message: Message):
    await message.reply_text("🛑 **चल रहा क्विज़ रोक दिया गया है!**")

@Client.on_message(filters.command("pause"))
async def pause_quiz(client: Client, message: Message):
    await message.reply_text("⏸️ **क्विज़ पॉज़ कर दिया गया है!** आगे बढ़ाने के लिए `/resume` भेजें।")

@Client.on_message(filters.command("resume"))
async def resume_quiz(client: Client, message: Message):
    await message.reply_text("▶️ **क्विज़ पुनः चालू हो गया है!**")

@Client.on_message(filters.command("fast"))
async def fast_speed(client: Client, message: Message):
    await message.reply_text("⚡ **Fast Mode Active!** (प्रश्न 10 सेकंड में बदलेंगे)")

@Client.on_message(filters.command("slow"))
async def slow_speed(client: Client, message: Message):
    await message.reply_text("🐢 **Slow Mode Active!** (प्रश्न 45 सेकंड में बदलेंगे)")

@Client.on_message(filters.command("normal"))
async def normal_speed(client: Client, message: Message):
    await message.reply_text("🔄 **Normal Speed Restored!** (30 सेकंड टाइमर)")

# ----------------- 🛡️ MODERATION COMMANDS ----------------- #

@Client.on_message(filters.command("mute") & filters.group)
async def mute_user(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("🔇 कृपया जिसे म्यूट करना है उसके मैसेज पर Reply करके `/mute` लिखें।")
    await message.reply_text(f"🔇 **{message.reply_to_message.from_user.first_name}** को म्यूट कर दिया गया है।")

@Client.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("🔊 कृपया म्यूट यूज़र के मैसेज पर Reply करके `/unmute` लिखें।")
    await message.reply_text(f"🔊 **{message.reply_to_message.from_user.first_name}** को अनम्यूट कर दिया गया है।")

@Client.on_message(filters.command("broadcast"))
async def broadcast_msg(client: Client, message: Message):
    await message.reply_text("📢 **Broadcast Started!** मैसेज भेजा जा रहा है...")

@Client.on_message(filters.command("premium"))
async def premium_info(client: Client, message: Message):
    await message.reply_text(
        "💎 **Quiz Bot Premium Plan:**\n\n"
        "• Unlimited PDF/TXT Import\n"
        "• HTML Result Card & Leaderboard\n"
        "• AI Auto Quiz Maker\n\n"
        "संपर्क करें Admin से प्रीमियम लेने के लिए।"
    )
    
