import os
import re
import json
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import PyPDF2

# config.py से GROQ_API_KEY लाएगा
from config import GROQ_API_KEY


# ----------------- GROQ AI HELPER FUNCTION ----------------- #

def get_mcqs_from_groq(text):
    """Groq AI का उपयोग करके टेक्स्ट में से MCQ निकालता है"""
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)

        prompt = f"""
Extract all Multiple Choice Questions (MCQs) from the text below.
Format the output strictly as a JSON array of objects.
Do NOT output markdown formatting like ```json, just raw JSON.

JSON Structure:
[
  {{
    "question": "Question text here (max 250 chars)",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_id": 0
  }}
]

Note:
- correct_id must be 0 for Option A, 1 for Option B, 2 for Option C, 3 for Option D.
- Limit max 10 questions per request.

Text Content:
{text[:4000]}
"""

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2
        )

        res_text = response.choices[0].message.content.strip()
        res_text = re.sub(r"```json\s*|\s*```", "", res_text)
        
        return json.loads(res_text)
    except Exception as e:
        print(f"Groq API Error: {e}")
        return []


# ----------------- 1. OLD PDF IMPORT COMMAND ----------------- #

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
            text += page.extract_text() or ""
            
        if os.path.exists(doc):
            os.remove(doc)

        await msg.edit_text(f"✅ **PDF Processed Successfully!**\nTotal Extracted Characters: {len(text)}\n\n/create से अब क्विज़ जनरेट करें।")
    except Exception as e:
        if os.path.exists(doc):
            os.remove(doc)
        await msg.edit_text(f"❌ Error Reading PDF: {str(e)}")


# ----------------- 2. NEW GROQ AI PDF TO MCQ COMMAND ----------------- #

@Client.on_message(filters.command("pdf2mcq"))
async def pdf2mcq_cmd(client: Client, message: Message):
    reply_msg = message.reply_to_message
    doc = reply_msg.document if reply_msg and reply_msg.document else message.document

    if not doc or not doc.file_name.lower().endswith('.pdf'):
        return await message.reply_text("⚠️ किसी PDF फ़ाइल पर रिप्लाई करते हुए या अटैच करके `/pdf2mcq` लिखें!")

    status_msg = await message.reply_text("📥 **PDF डाउनलोड की जा रही है... ⏳**")

    try:
        import pypdf
        file_path = await client.download_media(doc)
        
        await status_msg.edit_text("🤖 **Groq AI द्वारा PDF से प्रश्न निकाले जा रहे हैं... ⏳**")
        
        reader = pypdf.PdfReader(file_path)
        extracted_text = "".join([page.extract_text() + "\n" for page in reader.pages[:5] if page.extract_text()])

        if os.path.exists(file_path):
            os.remove(file_path)

        if not extracted_text.strip():
            return await status_msg.edit_text("❌ PDF से टेक्स्ट नहीं निकाला जा सका।")

        mcq_list = get_mcqs_from_groq(extracted_text)

        if not mcq_list:
            return await status_msg.edit_text("❌ Groq AI को इस PDF में क्विज़ प्रश्न नहीं मिले।")

        await status_msg.edit_text(f"✅ **Groq AI ने {len(mcq_list)} प्रश्न पाए! क्विज़ भेजी जा रही है... 🚀**")
        await asyncio.sleep(1)
        await status_msg.delete()

        for mcq in mcq_list:
            try:
                await client.send_poll(
                    chat_id=message.chat.id,
                    question=mcq["question"][:250],
                    options=[opt[:100] for opt in mcq["options"]],
                    is_anonymous=False,
                    type="quiz",
                    correct_option_id=mcq["correct_id"]
                )
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Poll Send Error: {e}")

    except Exception as e:
        await status_msg.edit_text(f"❌ त्रुटि: `{e}`")


# ----------------- 3. PDF TO TXT CONVERTER COMMAND ----------------- #

@Client.on_message(filters.command("pdf2txt"))
async def pdf_to_txt_cmd(client: Client, message: Message):
    reply_msg = message.reply_to_message
    doc = reply_msg.document if reply_msg and reply_msg.document else message.document

    if not doc or not doc.file_name.lower().endswith('.pdf'):
        return await message.reply_text("⚠️ कृपया किसी PDF फ़ाइल को रिप्लाई करते हुए या अटैच करके `/pdf2txt` लिखें!")

    status_msg = await message.reply_text("📥 **PDF डाउनलोड हो रही है, कृपया प्रतीक्षा करें... ⏳**")

    try:
        import pypdf
        file_path = await client.download_media(doc)
        
        await status_msg.edit_text("⚙️ **PDF से टेक्स्ट निकाला जा रहा है... ⏳**")
        
        reader = pypdf.PdfReader(file_path)
        extracted_text = "".join([page.extract_text() + "\n" for page in reader.pages if page.extract_text()])

        if os.path.exists(file_path):
            os.remove(file_path)

        if not extracted_text.strip():
            return await status_msg.edit_text("❌ इस PDF से कोई टेक्स्ट नहीं निकाला जा सका।")

        txt_filename = f"{doc.file_name.rsplit('.', 1)[0]}.txt"
        with open(txt_filename, "w", encoding="utf-8") as f:
            f.write(extracted_text)

        await message.reply_document(
            document=txt_filename,
            caption="✅ **आपकी PDF फ़ाइल को सफलतापूर्वक TXT में कंवर्ट कर दिया गया है!**"
        )
        os.remove(txt_filename)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ त्रुटि: `{e}`")
    
