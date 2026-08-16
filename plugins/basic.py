import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Client.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    welcome_text = (
        f"👋 **नमस्ते {message.from_user.first_name}!**\n\n"
        "मैं एक ऑल-इन-वन यूटिलिटी और क्विज़ टेलीग्राम बॉट हूँ। 🤖\n\n"
        "नीचे दिए गए बटन या `/help` कमांड का उपयोग करके मेरी सभी सुविधाओं को देखें।"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 हेल्प एवं कमांड्स", callback_data="help_menu")]
    ])
    await message.reply_text(welcome_text, reply_markup=keyboard)


@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    help_text = (
        "🛠 **बॉट कमांड्स और फीचर्स:**\n\n"
        "👥 `/users` - रजिस्टर्ड यूज़र्स देखें\n"
        "💬 `/chats` - एक्टिव चैट्स देखें\n"
        "📄 `/banlist` - बैन यूज़र्स की लिस्ट\n"
        "🚪 `/leavegrp` - ग्रुप छोड़ें\n"
        "📅 `/schedule` - क्विज़ शेड्यूल करें\n"
        "🖥 `/html` - HTML to TXT कंवर्टर\n"
        "📄 `/tx2html` - TXT to HTML कंवर्टर\n"
        "📘 `/pdf2txt` - PDF to TXT कंवर्टर\n"
        "📷 `/pdf2mcq` - इमेज/बुक से MCQ बनाएं\n"
        "🔑 `/auth` - एडमिन ऑथराइज़ करें\n"
        "🧹 `/rem_auth` - ऑथराइज़ एडमिन हटाएं\n"
        "🤖 `/aiquiz` - ऑटो क्विज़ AI\n"
        "🔇 `/mute` - मेंबर म्यूट करें\n"
        "🔊 `/unmute` - मेंबर अनम्यूट करें\n"
    )
    await message.reply_text(help_text)


@Client.on_callback_query(filters.regex("help_menu"))
async def help_callback(client: Client, callback_query: CallbackQuery):
    help_text = (
        "🛠 **बॉट कमांड्स और फीचर्स:**\n\n"
        "👥 `/users` - रजिस्टर्ड यूज़र्स देखें\n"
        "💬 `/chats` - एक्टिव चैट्स देखें\n"
        "📄 `/banlist` - बैन यूज़र्स की लिस्ट\n"
        "🚪 `/leavegrp` - ग्रुप छोड़ें\n"
        "📅 `/schedule` - क्विज़ शेड्यूल करें\n"
        "🖥 `/html` - HTML to TXT कंवर्टर\n"
        "📄 `/tx2html` - TXT to HTML कंवर्टर\n"
        "📘 `/pdf2txt` - PDF to TXT कंवर्टर\n"
        "📷 `/pdf2mcq` - इमेज/बुक से MCQ बनाएं\n"
        "🔑 `/auth` - एडमिन ऑथराइज़ करें\n"
        "🧹 `/rem_auth` - ऑथराइज़ एडमिन हटाएं\n"
        "🤖 `/aiquiz` - ऑटो क्विज़ AI\n"
        "🔇 `/mute` - मेंबर म्यूट करें\n"
        "🔊 `/unmute` - मेंबर अनम्यूट करें\n"
    )
    await callback_query.message.edit_text(help_text)

@Client.on_message(filters.command("users"))
async def users_cmd(client: Client, message: Message):
    await message.reply_text("👥 **कुल पंजीकृत यूज़र्स:** डाटाबेस कनेक्ट होने पर उपलब्ध होगा।")

@Client.on_message(filters.command("chats"))
async def chats_cmd(client: Client, message: Message):
    await message.reply_text("💬 **कुल एक्टिव चैट्स:** डाटाबेस कनेक्ट होने पर उपलब्ध होगा।")
    
