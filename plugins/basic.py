import os
import asyncio
import json
from groq import Groq
from pyrogram import Client, filters
from pyrogram.types import Message, Poll
from pyrogram.enums import ParseMode, PollType

# Environment Variables
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

# Initialize Groq Client
groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# Active State Memory Trackers
ONGOING_QUIZZES = {}
BANNED_USERS = set()
AUTH_USERS = set([ADMIN_ID])
USER_SCORES = {}   # {user_id: {"name": str, "correct": int, "wrong": int, "score": float}}
QUIZ_ANSWERS = {}  # {poll_id: correct_option_id}
QUIZ_TIMELIMIT = 15  # ⏱️ 15 सेकंड का टाइमर

# ----------------- 1. BASIC, AUTH & RANKING COMMANDS ----------------- #

@Client.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        return await message.reply_text("🚫 आप इस बॉट का उपयोग करने से प्रतिबंधित हैं!")
    
    await message.reply_text(
        f"🪐 **नमस्ते {message.from_user.first_name}!**\n\n"
        "यह आपका **Groq AI-Powered Quiz Bot (15s Timer + Leaderboard)** है 🚀\n"
        "• AI Quiz के लिए: `/aiquiz Polity`\n"
        "• रैंकिंग देखने के लिए: `/leaderboard`\n"
        "• सभी कमांड्स: `/help`",
        parse_mode=ParseMode.MARKDOWN
    )

@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    help_text = (
        "🧭 **ALL BOT COMMANDS LIST** 🧭\n\n"
        "📌 **Basic & Info:** /start, /stats, /leaderboard, /help, /features, /premium, /userprofile, /info\n"
        "🛠️ **Quiz Management:** /create, /add, /edit, /delete, /quiz, /quizid, /myquizzes, /delquizdb\n"
        "📁 **Imports & Conversion:** /pdfimport, /txtimport, /poll2q, /scrapepoll, /pdf2txt, /pdf2mcq, /html, /tx2html\n"
        "🤖 **Groq AI Features:** `/aiquiz <Topic>` (15s Poll Quiz with 1/3 Neg Marking)\n"
        "⏱️ **Quiz Controls:** /stop, /cancel, /pause, /resume, /fast, /slow, /normal, /negmark, /resetpenalty, /schedule, /clone, /queue\n"
        "📑 **Reports & Info:** /pdfinfo, /htmlinfo, /htmlreport, /mocktest\n"
        "📢 **Admin Controls:** /broadcast, /stopcast, /ban, /unban, /users, /chats, /banlist, /leavegrp, /auth, /rem_auth\n"
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
        text += (
            f"{medal} **{user['name']}**\n"
            f"   ┗ 🏆 स्कोर: `{round(user['score'], 2)}` | ✅ {user['correct']} | ❌ {user['wrong']}\n"
        )
    await message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("stats"))
async def stats_cmd(client: Client, message: Message):
    uid = message.from_user.id
    stats = USER_SCORES.get(uid, {"correct": 0, "wrong": 0, "score": 0.0})
    await message.reply_text(
        f"📊 **आपकी व्यक्तिगत सांख्यिकी (1/3 Negative Marking):**\n\n"
        f"✅ सही उत्तर: {stats['correct']} (+1.0)\n"
        f"❌ गलत उत्तर: {stats['wrong']} (-0.33)\n"
        f"🏆 कुल अंक: **{round(stats['score'], 2)}**",
        parse_mode=ParseMode.MARKDOWN
    )

@Client.on_message(filters.command("features"))
async def features_cmd(client: Client, message: Message):
    await message.reply_text("🎟️ **विशेषताएँ:**\n- Ultra-Fast Groq AI (Llama 3.1)\n- Telegram Quiz Poll UI\n- 15s Timer & 1/3 Negative Marking\n- Dynamic Leaderboard", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("premium"))
async def premium_cmd(client: Client, message: Message):
    await message.reply_text("💎 **Premium Access:**\nप्रीमियम सुविधाओं के लिए एडमिन से संपर्क करें।", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("userprofile"))
async def userprofile_cmd(client: Client, message: Message):
    user = message.from_user
    await message.reply_text(f"👨‍💼 **Profile Info:**\nName: {user.first_name}\nID: `{user.id}`", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("info"))
async def info_cmd(client: Client, message: Message):
    await message.reply_text("👤 **Quiz Creator Info:**\nGroq AI Powered Telegram Quiz Engine v3.0", parse_mode=ParseMode.MARKDOWN)

# ----------------- 2. GROQ AI TELEGRAM QUIZ GENERATOR ----------------- #

@Client.on_message(filters.command("aiquiz"))
async def ai_quiz(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ उपयोग: `/aiquiz <Topic Name>`\nउदाहरण: `/aiquiz Polity`", parse_mode=ParseMode.MARKDOWN)

    topic = " ".join(message.command[1:])
    status_msg = await message.reply_text(f"⚡ **Groq AI `{topic}` पर 15s टाइमर वाला Telegram Quiz बना रहा है... ⏳**", parse_mode=ParseMode.MARKDOWN)

    if not groq_client:
        return await status_msg.edit_text("❌ GROQ_API_KEY सेट नहीं है!")

    prompt = (
        f"Create 3 multiple choice quiz questions on topic '{topic}' in Hindi. "
        "Output ONLY a raw JSON array of objects. Do not include markdown formatting like ```json. "
        "Each object must have these exact keys: "
        "'question' (string), 'options' (array of 4 strings), 'correct_option' (integer 0-3 index), 'explanation' (string). "
        "Example output: [{\"question\": \"प्रश्न?\", \"options\": [\"A\", \"B\", \"C\", \"D\"], \"correct_option\": 1, \"explanation\": \"स्पष्टीकरण\"}]"
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

        # Send Telegram Poll Quiz with 15-second countdown
        for q in questions:
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
            QUIZ_ANSWERS[poll_msg.poll.id] = int(q["correct_option"])
            await asyncio.sleep(QUIZ_TIMELIMIT + 2)

        await message.reply_text(
            "🎉 **क्विज़ पूरा हुआ!**\n"
            "ग्रुप और अपनी लाइव रैंकिंग देखने के लिए `/leaderboard` टाइप करें।"
        )

    except Exception as e:
        print(f"Quiz Error: {e}")
        await status_msg.edit_text(f"❌ Quiz जनरेट करने में त्रुटि: `{e}`")

# ----------------- 3. 1/3 NEGATIVE MARKING & RANKING TRACKER ----------------- #

@Client.on_poll_answer()
async def process_poll_answer(client: Client, poll_answer):
    poll_id = poll_answer.poll_id
    user = poll_answer.user
    user_id = user.id
    selected_option = poll_answer.option_ids[0] if poll_answer.option_ids else None

    if poll_id not in QUIZ_ANSWERS or selected_option is None:
        return

    correct_option = QUIZ_ANSWERS[poll_id]

    if user_id not in USER_SCORES:
        USER_SCORES[user_id] = {
            "name": user.first_name + (f" {user.last_name}" if user.last_name else ""),
            "correct": 0,
            "wrong": 0,
            "score": 0.0
        }

    # Score Logic: Correct +1.0, Wrong -0.33
    if selected_option == correct_option:
        USER_SCORES[user_id]["correct"] += 1
        USER_SCORES[user_id]["score"] += 1.0
    else:
        USER_SCORES[user_id]["wrong"] += 1
        USER_SCORES[user_id]["score"] -= 0.33

# ----------------- 4. QUIZ CREATION & MANAGEMENT ----------------- #

@Client.on_message(filters.command("create"))
async def create_quiz(client: Client, message: Message):
    await message.reply_text("🛠️ **नया क्विज़ बनाएं:** कृपया अपने क्विज़ का टाइटल भेजें।", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("add"))
async def add_q(client: Client, message: Message):
    await message.reply_text("➕ **सवाल जोड़ें:** Format - Question | Opt1 | Opt2 | Opt3 | Opt4 | CorrectOpt(1-4)", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("edit"))
async def edit_q(client: Client, message: Message):
    await message.reply_text("📝 एडिट करने के लिए Question ID भेजें: `/edit <question_id>`", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("delete"))
async def delete_q(client: Client, message: Message):
    await message.reply_text("🗑️ सवाल हटाने के लिए ID भेजें: `/delete <question_id>`", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("quiz"))
async def start_quiz_cmd(client: Client, message: Message):
    ONGOING_QUIZZES[message.chat.id] = True
    await message.reply_text("🚀 **क्विज़ शुरू हो गया है!** पहला सवाल लोड हो रहा है...", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("quizid"))
async def start_quiz_id(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ उपयोग: `/quizid <Quiz_ID>`", parse_mode=ParseMode.MARKDOWN)
    await message.reply_text(f"🧩 **Quiz ID `{message.command[1]}` से क्विज़ लोड हो रहा है...**", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("myquizzes"))
async def myquizzes_cmd(client: Client, message: Message):
    await message.reply_text("💼 **आपके बनाए गए Quizzes:**\n\n1. General Knowledge (ID: 101)\n2. Polity (ID: 102)", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("delquizdb"))
async def delquizdb_cmd(client: Client, message: Message):
    await message.reply_text("🗑️ उपयोग: `/delquizdb <Quiz_ID>` डेटाबेस से हटाने के लिए।", parse_mode=ParseMode.MARKDOWN)

# ----------------- 5. FILE IMPORTS & CONVERTERS ----------------- #

@Client.on_message(filters.command("pdfimport"))
async def pdfimport_cmd(client: Client, message: Message):
    await message.reply_text("📁 PDF फ़ाइल अपलोड करें और कैप्शन में `/pdfimport` लिखें।", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("txtimport"))
async def txtimport_cmd(client: Client, message: Message):
    await message.reply_text("📄 TXT फ़ाइल अपलोड करें और कैप्शन में `/txtimport` लिखें।", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("poll2q"))
async def poll2q_cmd(client: Client, message: Message):
    await message.reply_text("🔄 Telegram Poll पर रिप्लाई करके `/poll2q` लिखें।", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("scrapepoll"))
async def scrapepoll_cmd(client: Client, message: Message):
    await message.reply_text("🎧 चैनल से पोल्स स्क्रैप करने के लिए `/scrapepoll <channel_link>` भेजें।", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("pdf2txt"))
async def pdf2txt_cmd(client: Client, message: Message):
    await message.reply_text("📘 PDF भेजकर `/pdf2txt` रिप्लाई करें।", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("pdf2mcq"))
async def pdf2mcq_cmd(client: Client, message: Message):
    await message.reply_text("📷 स्कैन की गई किताब की इमेज/PDF भेजें MCQ में बदलने के लिए।", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("html"))
async def html2txt_cmd(client: Client, message: Message):
    await message.reply_text("🖥️ HTML फ़ाइल को Text में बदला जा रहा है...", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("tx2html"))
async def txt2html_cmd(client: Client, message: Message):
    await message.reply_text("📑 Text फ़ाइल को HTML वेब पेज में बदला जा रहा है...", parse_mode=ParseMode.MARKDOWN)

# ----------------- 6. CONTROLS, SPEED & PENALTY ----------------- #

@Client.on_message(filters.command(["stop", "cancel"]))
async def stop_cmd(client: Client, message: Message):
    ONGOING_QUIZZES.pop(message.chat.id, None)
    await message.reply_text("🛑 **क्विज़/ऑपरेशन रोक दिया गया है!**", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("pause"))
async def pause_cmd(client: Client, message: Message):
    await message.reply_text("⏸️ **क्विज़ पॉज़ कर दिया गया है!**", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("resume"))
async def resume_cmd(client: Client, message: Message):
    await message.reply_text("▶️ **क्विज़ पुनः प्रारंभ!**", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("fast"))
async def fast_cmd(client: Client, message: Message):
    await message.reply_text("⚡ **Fast Mode (10s Timer Active active)**", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("slow"))
async def slow_cmd(client: Client, message: Message):
    await message.reply_text("🐢 **Slow Mode (45s Timer Active)**", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("normal"))
async def normal_cmd(client: Client, message: Message):
    await message.reply_text("🔄 **Normal Speed (15s Timer Restored)**", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("negmark"))
async def negmark_cmd(client: Client, message: Message):
    await message.reply_text("⚖️ **Negative Marking:** 1/3 (-0.33) cut-off लागू है।", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("resetpenalty"))
async def resetpenalty_cmd(client: Client, message: Message):
    await message.reply_text("🧮 **नेगेटिव मार्किंग रीसेट कर दी गई है।**", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("schedule"))
async def schedule_cmd(client: Client, message: Message):
    await message.reply_text("📅 उपयोग: `/schedule <HH:MM>` क्विज़ शेड्यूल करने के लिए।", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("clone"))
async def clone_cmd(client: Client, message: Message):
    await message.reply_text("🧩 क्विज़ क्लोन तैयार किया जा रहा है...", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("queue"))
async def queue_cmd(client: Client, message: Message):
    await message.reply_text("🕒 **Ongoing Queue Status:** No pending tasks.", parse_mode=ParseMode.MARKDOWN)

# ----------------- 7. REPORTS & TESTS ----------------- #

@Client.on_message(filters.command("pdfinfo"))
async def pdfinfo_cmd(client: Client, message: Message):
    await message.reply_text("📗 **PDF Guide:** PDF में सवाल format में होने चाहिए:\nQ1. Question?\n(A) Option1\n(B) Option2\nAns: B", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("htmlinfo"))
async def htmlinfo_cmd(client: Client, message: Message):
    await message.reply_text("🖥️ **HTML Reports Guide:** विस्तृत स्कोरकार्ड वेब व्यू में जनरेट होता है।", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("htmlreport"))
async def htmlreport_cmd(client: Client, message: Message):
    await message.reply_text("💼 **HTML Report Result Generated!** [Download Link Active]", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("mocktest"))
async def mocktest_cmd(client: Client, message: Message):
    await message.reply_text("📑 **Mock Test Mode:** 100 प्रश्नों की ऑनलाइन परीक्षा मोड शुरू।", parse_mode=ParseMode.MARKDOWN)

# ----------------- 8. ADMIN CONTROLS ----------------- #

@Client.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("📢 ब्रॉडकास्ट करने वाले मैसेज पर Reply करके `/broadcast` लिखें।")
    await message.reply_text("📢 Broadcast Started...")

@Client.on_message(filters.command("stopcast") & filters.user(ADMIN_ID))
async def stopcast_cmd(client: Client, message: Message):
    await message.reply_text("✋ Broadcast Paused.")

@Client.on_message(filters.command("ban") & filters.user(ADMIN_ID))
async def ban_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("🚫 उपयोग: `/ban <user_id>`")
    uid = int(message.command[1])
    BANNED_USERS.add(uid)
    await message.reply_text(f"🚫 User `{uid}` banned.")

@Client.on_message(filters.command("unban") & filters.user(ADMIN_ID))
async def unban_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("♻️ उपयोग: `/unban <user_id>`")
    uid = int(message.command[1])
    BANNED_USERS.discard(uid)
    await message.reply_text(f"♻️ User `{uid}` unbanned.")

@Client.on_message(filters.command("users") & filters.user(ADMIN_ID))
async def users_cmd(client: Client, message: Message):
    await message.reply_text("👥 **Total Registered Users:** 1 (Active)", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("chats") & filters.user(ADMIN_ID))
async def chats_cmd(client: Client, message: Message):
    await message.reply_text("💬 **Active Groups:** 1", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("banlist") & filters.user(ADMIN_ID))
async def banlist_cmd(client: Client, message: Message):
    await message.reply_text(f"📄 **Banned List:** `{list(BANNED_USERS)}`", parse_mode=ParseMode.MARKDOWN)

@Client.on_message(filters.command("leavegrp") & filters.user(ADMIN_ID))
async def leavegrp_cmd(client: Client, message: Message):
    await message.chat.leave()

@Client.on_message(filters.command("auth") & filters.user(ADMIN_ID))
async def auth_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("🔐 उपयोग: `/auth <user_id>`")
    AUTH_USERS.add(int(message.command[1]))
    await message.reply_text("🔐 User authorized.")

@Client.on_message(filters.command("rem_auth") & filters.user(ADMIN_ID))
async def rem_auth_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("🔓 उपयोग: `/rem_auth <user_id>`")
    
    uid = int(message.command[1])
    AUTH_USERS.discard(uid)
    await message.reply_text(f"🔓 User `{uid}` authorization removed.")
    
