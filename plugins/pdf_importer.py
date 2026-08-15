from pyrogram import Client, filters
from pyrogram.types import Message
import PyPDF2

@Client.on_message(filters.command("pdfimport"))
async def pdf_import_cmd(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply_text("📁 कृपया किसी PDF फ़ाइल का उत्तर (Reply) देते हुए `/pdfimport` कमांड भेजें।")
    
    msg = await message.reply_text("⏳ Processing PDF File...")
    doc = await message.reply_to_message.download()
    
    try:
        reader = PyPDF2.PdfReader(doc)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
            
        await msg.edit_text(f"✅ **PDF Processed Successfully!**\nTotal Extracted Characters: {len(text)}\n\n/create से अब क्विज़ जनरेट करें।")
    except Exception as e:
        await msg.edit_text(f"❌ Error Reading PDF: {str(e)}")
      
