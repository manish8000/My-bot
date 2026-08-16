import os
import asyncio
import json
from groq import Groq
from motor.motor_asyncio import AsyncIOMotorClient

from pyrogram import Client, filters
from pyrogram.types import Message, Poll, ChatPermissions
from pyrogram.enums import ParseMode, PollType
from pyrogram.raw import types

# ----------------- CONFIGURATION ----------------- #
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
MONGO_URI = os.environ.get("MONGO_URI", "")

groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

if MONGO_URI:
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    db = mongo_client["QuizBotDB"]
    users_col = db["users"]
    chats_col = db["chats"]
else:
    users_col = None
    chats_col = None

ONGOING_QUIZZES = {}
PAUSED_QUIZZES = set()
BANNED_USERS = set()
AUTH_USERS = set([ADMIN_ID])
USER_SCORES = {}   
QUIZ_ANSWERS = {}  
QUIZ_TIMELIMIT = 15  

async def register_user_chat(message: Message):
    if users_col is not None and message.from_user:
        await users_col.update_one(
            {"_id": message.from_user.id},
            {"$set": {"name": message.from_user.first_name, "username": message.from_user.username}},
            upsert=True
        )
    if chats_col is not None and message.chat:
        await chats_col.update_one(
            {"_id": message.chat.id},
            {"$set": {"title": message.chat.title or "Private"}},
            upsert=True
        )

# ----------------- 1. BASIC COMMANDS ----------------- #

@Client.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    if message.from_user.id in BANNED_USERS:
        return await message.reply_text("🚫 आप इस बॉट का उपयोग करने से प्रतिबंधित हैं!")
    
    await register_user_chat(message)
    await message.reply_text(
        f"🪐 **नमस्ते {message.from_user.first_name}!**\n\n"
        "यह आपका **Groq AI-Powered Advanced Quiz Bot** है! 🚀\n"
        "• AI Quiz के लिए: `/aiquiz Polity`\n"
        "• रैंकिंग देखने के लिए: `/leaderboard`\n"
        "• सभी कमांड्स: `/help`",
        parse_mode=ParseMode.MARKDOWN
    )

@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    help_text = (
        "🧭 **ALL BOT COMMANDS LIST** 🧭\n\n"
        "📌 **Basic & Info:** /start, /stats, /leaderboard, /ranking, /top, /help, /features, /premium, /userprofile, /info\n\n"
        "🛠️ **Quiz Management:** /create, /add, /edit, /delete, /quiz, /quizid, /myquizzes, /delquizdb\n\n"
        "📁 **Imports & Conversion:** /pdfimport, /txtimport, /poll2q, /scrapepoll, /pdf2txt, /pdf2mcq, /html, /tx2html\n\n"
        "🤖 **Groq AI Features:** `/aiquiz <Topic>`\n\n"
        "⏱️ **Quiz Controls:** /stop, /cancel, /pause, /resume, /fast, /slow, /normal, /negmark, /resetpenalty, /schedule, /clone, /queue\n\n"
        "📑 **Reports & Info:** /pdfinfo, /htmlinfo, /htmlreport, /mocktest\n\n"
        "📢 **Admin Controls:** /broadcast, /stopcast, /ban, /unban, /users, /chats, /banlist, /leavegrp, /auth, /rem_auth\n\n"
        "🛡️ **Moderation:** /mute, /unmute"
    )
    await message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command(["leaderboard", "ranking", "top"]))
async def leaderboard_cmd(client: Client, message: Message):
    if not USER_SCORES:
        return await message.reply_text("🏆 **लीडरबोर्ड:** अभी तक किसी ने क्विज़ में भाग नहीं लिया है!")

    sorted_users = sorted(USER_SCORES.values(), key=lambda x: x["score"], reverse=True)
    text = "🏆 **QUIZ LEADERBOARD & RANKING** 🏆\n\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    for idx, user in enumerate(sorted_users[:10]):
        medal = medals[idx] if idx < len(medals) else f"#{idx+1}"
        text += f"{medal} **{user['name']}**\n   ┗ 🏆 स्कोर: `{round(user['score'], 2)}` | ✅ {user['correct']} | ❌ {user['wrong']}\n"
    await message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("stats"))
async def stats_cmd(client: Client, message: Message):
    stats = USER_SCORES.get(message.from_user.id, {"correct": 0, "wrong": 0, "score": 0.0})
    await message.reply_text(
        f"📊 **आपकी व्यक्तिगत सांख्यिकी:**\n\n✅ सही उत्तर: {stats['correct']} (+1.0)\n❌ गलत उत्तर: {stats['wrong']} (-0.33)\n🏆 कुल अंक: **{round(stats['score'], 2)}**",
        parse_mode=ParseMode.MARKDOWN
    )

# ----------------- 2. GROQ AI QUIZ ENGINE ----------------- #

@Client.on_message(filters.command("aiquiz"))
async def ai_quiz(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ उपयोग: `/aiquiz <Topic Name>`\nउदाहरण: `/aiquiz Polity`", parse_mode=ParseMode.MARKDOWN)

    topic = " ".join(message.command[1:])
    status_msg = await message.reply_text(f"⚡ **Groq AI `{topic}` पर {QUIZ_TIMELIMIT}s टाइमर वाला Quiz बना रहा है... ⏳**", parse_mode=ParseMode.MARKDOWN)

    if not groq_client:
        return await status_msg.edit_text("❌ GROQ_API_KEY सेट नहीं है!")

    prompt = (
        f"Create 3 multiple choice quiz questions on topic '{topic}' in Hindi. "
        "Output ONLY a raw JSON array of objects. Do not include markdown formatting. "
        "Each object must have these exact keys: "
        "'question' (string), 'options' (array of 4 strings), 'correct_option' (integer 0-3 index), 'explanation' (string)."
    )

    try:
        loop = asyncio.get_event_loop()
        completion = await loop.run_in_executor(
            None,
            lambda: groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
        )
        
        raw_text = completion.choices[0].message.content.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        
        questions = json.loads(raw_text.strip())
        await status_msg.delete()

        ONGOING_QUIZZES[message.chat.id] = True

        for q in questions:
            if not ONGOING_QUIZZES.get(message.chat.id):
                break
            while message.chat.id in PAUSED_QUIZZES:
                await asyncio.sleep(2)

            poll_msg = await client.send_poll(
                chat_id=message.chat.id,
                question=q["question"] + f"\n\n⏱️ समय: {QUIZ_TIMELIMIT}s | ⚖️ (-1/3 Mark)",
                options=q["options"],
                is_anonymous=False,
                type=PollType.QUIZ,
                correct_option_id=int(q["correct_option"]),
                explanation=q.get("explanation", "1/3 नेगेटिव मार्किंग लागू है!"),
                open_period=QUIZ_TIMELIMIT
            )
            QUIZ_ANSWERS[str(poll_msg.poll.id)] = int(q["correct_option"])
            await asyncio.sleep(QUIZ_TIMELIMIT + 2)

        ONGOING_QUIZZES.pop(message.chat.id, None)
        await message.reply_text("🎉 **क्विज़ पूरा हुआ!**\nरैंकिंग देखने के लिए `/leaderboard` टाइप करें।")

    except Exception as e:
        await status_msg.edit_text(f"❌ Quiz जनरेट करने में त्रुटि: `{e}`")

# ----------------- 3. POLL SCORE TRACKER (FIXED) ----------------- #

@Client.on_raw_update()
async def process_raw_poll_answer(client: Client, update, users, chats):
    if isinstance(update, types.UpdateMessagePollVote):
        poll_id = str(update.poll_id)
        user_id = update.user_id
        
        if poll_id not in QUIZ_ANSWERS or not update.options:
            return

        # Bytes को safe तरीके से integer में बदलने का फिक्स
        raw_opt = update.options[0]
        if isinstance(raw_opt, bytes):
            selected_option = int.from_bytes(raw_opt, byteorder="big")
        else:
            selected_option = int(raw_opt)

        correct_option = QUIZ_ANSWERS[poll_id]

        user_obj = users.get(user_id)
        user_name = f"User {user_id}"
        if user_obj:
            user_name = user_obj.first_name + (f" {user_obj.last_name}" if user_obj.last_name else "")

        if user_id not in USER_SCORES:
            USER_SCORES[user_id] = {"name": user_name, "correct": 0, "wrong": 0, "score": 0.0}

        if selected_option == correct_option:
            USER_SCORES[user_id]["correct"] += 1
            USER_SCORES[user_id]["score"] += 1.0
        else:
            USER_SCORES[user_id]["wrong"] += 1
            USER_SCORES[user_id]["score"] -= 0.33
            

# ----------------- 4. SPEED & CONTROLS ----------------- #

@Client.on_message(filters.command(["stop", "cancel"]))
async def stop_cmd(client: Client, message: Message):
    ONGOING_QUIZZES.pop(message.chat.id, None)
    PAUSED_QUIZZES.discard(message.chat.id)
    await message.reply_text("🛑 **क्विज़/ऑपरेशन रोक दिया गया है!**")

@Client.on_message(filters.command("pause"))
async def pause_cmd(client: Client, message: Message):
    PAUSED_QUIZZES.add(message.chat.id)
    await message.reply_text("⏸️ **क्विज़ पॉज़ कर दिया गया है!**")

@Client.on_message(filters.command("resume"))
async def resume_cmd(client: Client, message: Message):
    PAUSED_QUIZZES.discard(message.chat.id)
    await message.reply_text("▶️ **क्विज़ पुनः प्रारंभ!**")

@Client.on_message(filters.command("fast"))
async def fast_cmd(client: Client, message: Message):
    global QUIZ_TIMELIMIT
    QUIZ_TIMELIMIT = 10
    await message.reply_text("⚡ **Fast Mode (10s Timer Active)**")

@Client.on_message(filters.command("slow"))
async def slow_cmd(client: Client, message: Message):
    global QUIZ_TIMELIMIT
    QUIZ_TIMELIMIT = 45
    await message.reply_text("🐢 **Slow Mode (45s Timer Active)**")

@Client.on_message(filters.command("normal"))
async def normal_cmd(client: Client, message: Message):
    global QUIZ_TIMELIMIT
    QUIZ_TIMELIMIT = 15
    await message.reply_text("🔄 **Normal Speed (15s Timer Restored)**")
        
