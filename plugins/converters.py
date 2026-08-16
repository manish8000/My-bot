import os
from bs4 import BeautifulSoup
from pypdf import PdfReader
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("pdfimport") | filters.command("pdf2txt"))
async def pdfimport_cmd(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply_text("📁 **PDF फ़ाइल वाले मैसेज पर Reply करके यह कमांड लिखें!**")

    doc = message.reply_to_message.document
    if not doc.file_name.endswith(".pdf"):
        return await message.reply_text("❌ कृपया वैध PDF फ़ाइल भेजें!")

    msg = await message.reply_text("⏳ **PDF प्रोसेस की जा रही है...**")
    file_path = await message.reply_to_message.download()

    try:
        reader = PdfReader(file_path)
        extracted_text = ""
        for page in reader.pages:
            extracted_text += (page.extract_text() or "") + "\n"

        out_txt = file_path.replace(".pdf", ".txt")
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write(extracted_text)

        await message.reply_document(out_txt, caption="📄 **PDF से टेक्स्ट निकाला गया!**")
        os.remove(file_path)
        os.remove(out_txt)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ त्रुटि: `{e}`")

@Client.on_message(filters.command("txtimport"))
async def txtimport_cmd(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply_text("📄 **.TXT फ़ाइल पर Reply करें!**")
    
    file_path = await message.reply_to_message.download()
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    os.remove(file_path)
    await message.reply_text(f"✅ **TXT फ़ाइल लोड हुई!** ({len(content)} कैरेक्टर्स)")

@Client.on_message(filters.command("html"))
async def html2txt_cmd(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply_text("🖥️ **HTML फ़ाइल पर Reply करें!**")
    
    file_path = await message.reply_to_message.download()
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    out_file = file_path + ".txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(soup.get_text())
        
    await message.reply_document(out_file, caption="📑 HTML to Text Converted!")
    os.remove(file_path)
    os.remove(out_file)

@Client.on_message(filters.command("tx2html"))
async def txt2html_cmd(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply_text("📑 **TXT फ़ाइल पर Reply करें!**")
    
    file_path = await message.reply_to_message.download()
    with open(file_path, "r", encoding="utf-8") as f:
        raw = f.read()
    
    out_file = file_path + ".html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"<html><body><pre>{raw}</pre></body></html>")
        
    await message.reply_document(out_file, caption="🖥️ TXT to HTML Converted!")
    os.remove(file_path)
    os.remove(out_file)
  
