import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode, PollType

MONGO_URI = os.environ.get("MONGO_URI", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

if MONGO_URI:
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    db = mongo_client["QuizBotDB"]
    quizzes_col = db["quizzes"]
else:
    quizzes_col = None

# QUIZ CREATION & DATABASE COMMANDS

@Client.on_message(filters.command("create"))
async def create_quiz(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("🛠️ **उपयोग:** `/create <Quiz_Title>`", parse_mode=ParseMode.MARKDOWN)
    
    title = " ".join(message.command[1:])
    quiz_id = str(int(asyncio.get_event_loop().time()))[-6:]
    
    if quizzes_col is not None:
        await quizzes_col.insert_one({
            "quiz_id": quiz_id,
            "owner_id": message.from_user.id,
            "title": title,
            "questions": []
        })
        await message.reply_text(f"✅ **क्विज़ बनाया गया!**\n🆔 **Quiz ID:** `{quiz_id}`\n📌 **Title:** {title}\n\nअब सवाल जोड़ने के लिए `/add` का उपयोग करें।")
    else:
        await message.reply_text("❌ MongoDB डेटाबेस कनेक्टेड नहीं है!")

@Client.on_message(filters.command("add"))
async def add_q(client: Client, message: Message):
    raw_text = message.text.split(" ", 1)
    if len(raw_text) < 2 or "|" not in raw_text[1]:
        return await message.reply_text(
            "➕ **उपयोग फॉर्मेट:**\n`/add <Quiz_ID> | Question | Opt1 | Opt2 | Opt3 | Opt4 | CorrectIndex(0-3)`",
            parse_mode=ParseMode.MARKDOWN
        )

    parts = [p.strip() for p in raw_text[1].split("|")]
    if len(parts) < 7:
        return await message.reply_text("❌ गलत फॉर्मेट! कृपया सभी 7 फ़ील्ड्स प्रदान करें।")

    quiz_id, q_text, o1, o2, o3, o4, correct = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], int(parts[6])

    if quizzes_col is not None:
        q_obj = {"q": q_text, "options": [o1, o2, o3, o4], "correct": correct}
        res = await quizzes_col.update_one({"quiz_id": quiz_id}, {"$push": {"questions": q_obj}})
        if res.modified_count > 0:
            await message.reply_text(f"✅ **सवाल सफलतापूर्वक Quiz ID `{quiz_id}` में जोड़ा गया!**")
        else:
            await message.reply_text("❌ Quiz ID नहीं मिला!")

@Client.on_message(filters.command("delete"))
async def delete_q(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("🗑️ **उपयोग:** `/delete <Quiz_ID>`", parse_mode=ParseMode.MARKDOWN)
    quiz_id = message.command[1]
    if quizzes_col is not None:
        await quizzes_col.delete_one({"quiz_id": quiz_id})
        await message.reply_text(f"🗑️ **Quiz ID `{quiz_id}` हटा दिया गया है।**")

@Client.on_message(filters.command(["quiz", "quizid"]))
async def start_quiz_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ उपयोग: `/quizid <Quiz_ID>`", parse_mode=ParseMode.MARKDOWN)

    quiz_id = message.command[1]
    if quizzes_col is None:
        return await message.reply_text("❌ DB नॉट कनेक्टेड!")

    quiz = await quizzes_col.find_one({"quiz_id": quiz_id})
    if not quiz or not quiz.get("questions"):
        return await message.reply_text("❌ कोई क्विज़/सवाल नहीं मिला!")

    await message.reply_text(f"🚀 **क्विज़ शुरू: {quiz['title']}**")

    for q in quiz["questions"]:
        await client.send_poll(
            chat_id=message.chat.id,
            question=q["q"],
            options=q["options"],
            is_anonymous=False,
            type=PollType.QUIZ,
            correct_option_id=q["correct"],
            open_period=15
        )
        await asyncio.sleep(17)

@Client.on_message(filters.command("myquizzes"))
async def myquizzes_cmd(client: Client, message: Message):
    if quizzes_col is None:
        return await message.reply_text("❌ DB Not Connected!")
    
    cursor = quizzes_col.find({"owner_id": message.from_user.id})
    quizzes = await cursor.to_list(length=20)
    
    if not quizzes:
        return await message.reply_text("💼 **आपके पास कोई सेव किया हुआ क्विज़ नहीं है।**")

    msg = "💼 **आपके बनाए गए Quizzes:**\n\n"
    for q in quizzes:
        msg += f"• **{q['title']}** (ID: `{q['quiz_id']}`) - {len(q['questions'])} Questions\n"
    await message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
  
