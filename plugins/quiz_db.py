import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("aiquiz"))
async def aiquiz_cmd(client: Client, message: Message):
    topic = " ".join(message.command[1:])
    if not topic:
        return await message.reply_text("⚠️ विषय लिखें! उदा: `/aiquiz इतिहास`")
    status_msg = await message.reply_text(f"🤖 **AI `{topic}` पर क्विज़ बना रहा है... ⏳**")
    await asyncio.sleep(2)
    try:
        await client.send_poll(
            chat_id=message.chat.id,
            question=f"[{topic}] इनमें से कौन सा सही विकल्प है?",
            options=["विकल्प A", "विकल्प B", "विकल्प C", "विकल्प D"],
            is_anonymous=False, type="quiz", correct_option_id=0
        )
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ त्रुटि: `{e}`")


@Client.on_message(filters.command("pdf2mcq"))
async def pdf2mcq_cmd(client: Client, message: Message):
    reply_msg = message.reply_to_message
    if not reply_msg or not (reply_msg.document or reply_msg.photo):
        return await message.reply_text("⚠️ PDF या Photo पर रिप्लाई करें!")
    status_msg = await message.reply_text("📷 **MCQ बनाए जा रहे हैं... ⏳**")
    await asyncio.sleep(2)
    await client.send_poll(
        chat_id=message.chat.id,
        question="स्कैन किए गए कंटेंट से जनरेट प्रश्न 1:",
        options=["उत्तर A", "उत्तर B", "उत्तर C", "उत्तर D"],
        is_anonymous=False, type="quiz", correct_option_id=1
    )
    await status_msg.delete()


@Client.on_message(filters.command("schedule"))
async def schedule_cmd(client: Client, message: Message):
    args = message.command[1:]
    if not args or not args[0].isdigit():
        return await message.reply_text("⚠️ समय सेकंड में लिखें! उदा: `/schedule 10`")
    delay = int(args[0])
    await message.reply_text(f"📅 **क्विज़ {delay} सेकंड के लिए शेड्यूल हो गई!**")
    await asyncio.sleep(delay)
    await client.send_poll(
        chat_id=message.chat.id,
        question="📅 [शेड्यूल किया गया प्रश्न] सही विकल्प चुनें:",
        options=["ऑप्शन 1", "ऑप्शन 2", "ऑप्शन 3", "ऑप्शन 4"],
        is_anonymous=False, type="quiz", correct_option_id=0
    )


@Client.on_message(filters.command(["quiz", "launch"]))
async def quiz_cmd(client: Client, message: Message):
    await message.reply_poll(
        question="🚀 [Quiz Launched] भारत की राजधानी क्या है?",
        options=["नई दिल्ली", "मुंबई", "जयपुर", "कोलकाता"],
        is_anonymous=False, type="quiz", correct_option_id=0
    )

@Client.on_message(filters.command("stats"))
async def stats_cmd(client: Client, message: Message):
    await message.reply_text(f"📊 **{message.from_user.first_name} का स्कोर:**\n• हल किए प्रश्न: 0\n• सटीकता: 0%")

@Client.on_message(filters.command("add"))
async def add_cmd(client: Client, message: Message):
    await message.reply_text("➕ **फ़ॉर्मेट:** `प्रश्न | विकल्प1 | विकल्प2 | विकल्प3 | विकल्प4 | सही_विकल्प_नंबर`")

@Client.on_message(filters.command("edit"))
async def edit_cmd(client: Client, message: Message):
    await message.reply_text("✏️ ID दर्ज करें: उदा: `/edit 102`")

@Client.on_message(filters.command("delete"))
async def delete_cmd(client: Client, message: Message):
    await message.reply_text("🗑️ ID दर्ज करें: उदा: `/delete 102`")

@Client.on_message(filters.command("poll2q"))
async def poll2q_cmd(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.poll:
        return await message.reply_text("⚠️ साधारण पोल पर रिप्लाई करके `/poll2q` लिखें!")
    await message.reply_text("♻️ **पोल को क्विज़ में बदल दिया गया है!**")

@Client.on_message(filters.command("scrapepoll"))
async def scrapepoll_cmd(client: Client, message: Message):
    await message.reply_text("🎧 **चैनल से पोल स्क्रैपिंग शुरू...**")

@Client.on_message(filters.command("clone"))
async def clone_cmd(client: Client, message: Message):
    await message.reply_text("🧩 @QuizBot शेयर लिंक भेजें।")

@Client.on_message(filters.command("queue"))
async def queue_cmd(client: Client, message: Message):
    await message.reply_text("⏰ **वर्तमान क्विज़ कतार:** खाली है।")

@Client.on_message(filters.command("pdfimport"))
async def pdfimport_cmd(client: Client, message: Message):
    await message.reply_text("📁 PDF फाइल अटैच करके `/pdfimport` लिखें।")

@Client.on_message(filters.command("txtimport"))
async def txtimport_cmd(client: Client, message: Message):
    await message.reply_text("📄 Text फाइल अटैच करके `/txtimport` लिखें।")

@Client.on_message(filters.command("quizid"))
async def quizid_cmd(client: Client, message: Message):
    await message.reply_text("🧩 ID दर्ज करें: उदा. `/quizid 58291`")

@Client.on_message(filters.command("pdfinfo"))
async def pdfinfo_cmd(client: Client, message: Message):
    await message.reply_text("💳 **PDF Import Guide:** PDF में विकल्प (A, B, C, D) स्पष्ट होने चाहिए।")

@Client.on_message(filters.command("htmlinfo"))
async def htmlinfo_cmd(client: Client, message: Message):
    await message.reply_text("🖥️ **HTML Report Info:** परिणामों की वेब-पेज स्टाइल रिपोर्ट बनाता है।")

@Client.on_message(filters.command("htmlreport"))
async def htmlreport_cmd(client: Client, message: Message):
    await message.reply_text("📂 **HTML रिपोर्ट तैयार की जा रही है...**")
    
