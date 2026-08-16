import os
import re
from pyrogram import Client, filters
from pyrogram.types import Message

# PDF to TXT
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

        await message.reply_document(document=txt_filename, caption="✅ **PDF को TXT में कंवर्ट कर दिया गया है!**")
        os.remove(txt_filename)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ कंवर्ट करने में त्रुटि: `{e}`")


# TXT to HTML
@Client.on_message(filters.command(["tx2html", "txt2html"]))
async def txt_to_html_cmd(client: Client, message: Message):
    reply_msg = message.reply_to_message
    doc = reply_msg.document if reply_msg and reply_msg.document else message.document

    if not doc or not doc.file_name.lower().endswith('.txt'):
        return await message.reply_text("⚠️ कृपया किसी .txt फ़ाइल को रिप्लाई करते हुए या अटैच करके `/tx2html` लिखें!")

    status_msg = await message.reply_text("📥 **.txt फ़ाइल को HTML में कंवर्ट किया जा रहा है... ⏳**")
    try:
        file_path = await client.download_media(doc)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            txt_content = f.read()

        if os.path.exists(file_path):
            os.remove(file_path)

        html_content = "<!DOCTYPE html>\n<html>\n<head><meta charset='utf-8'><title>Converted Document</title></head>\n<body>\n"
        for p in txt_content.split("\n"):
            html_content += f"<p>{p.strip()}</p>\n" if p.strip() else "<br>\n"
        html_content += "</body>\n</html>"

        html_filename = f"{doc.file_name.rsplit('.', 1)[0]}.html"
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        await message.reply_document(document=html_filename, caption="🌐 **TXT फ़ाइल सफलतापूर्वक HTML में कंवर्ट हो गई है!**")
        os.remove(html_filename)
        await status_msg.delete()
    except Exception as e:
        await message.reply_text(f"❌ त्रुटि: `{e}`")


# HTML to TXT
@Client.on_message(filters.command(["html", "html2txt"]))
async def html_to_txt_cmd(client: Client, message: Message):
    reply_msg = message.reply_to_message
    doc = reply_msg.document if reply_msg and reply_msg.document else message.document

    if not doc or not doc.file_name.lower().endswith(('.html', '.htm')):
        return await message.reply_text("⚠️ कृपया किसी .html फ़ाइल को रिप्लाई करते हुए या अटैच करके `/html` लिखें!")

    status_msg = await message.reply_text("📥 **HTML फ़ाइल से टेक्स्ट निकाला जा रहा है... ⏳**")
    try:
        file_path = await client.download_media(doc)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            html_content = f.read()

        if os.path.exists(file_path):
            os.remove(file_path)

        clean_text = re.sub(r'<[^>]+>', '', html_content)
        clean_text = "\n".join([line.strip() for line in clean_text.splitlines() if line.strip()])

        if len(clean_text) > 3500:
            txt_filename = f"{doc.file_name.rsplit('.', 1)[0]}.txt"
            with open(txt_filename, "w", encoding="utf-8") as f:
                f.write(clean_text)
            await message.reply_document(document=txt_filename, caption="📝 **HTML का टेक्स्ट एक्सट्रैक्ट कर दिया गया है!**")
            os.remove(txt_filename)
            await status_msg.delete()
        else:
            await status_msg.edit_text(f"📝 **Extracted Text:**\n\n{clean_text}")
    except Exception as e:
        await message.reply_text(f"❌ त्रुटि: `{e}`")
        
