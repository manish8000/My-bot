from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions

AUTHORIZED_USERS = set()
BANNED_USERS = set()

@Client.on_message(filters.command("mute") & filters.group)
async def mute_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ जिस यूज़र को म्यूट करना है, उसके मैसेज पर रिप्लाई करें!")
    target_user = message.reply_to_message.from_user
    try:
        await client.restrict_chat_member(message.chat.id, target_user.id, ChatPermissions(can_send_messages=False))
        await message.reply_text(f"🔇 **{target_user.mention} को म्यूट कर दिया गया है।**")
    except Exception as e:
        await message.reply_text(f"❌ म्यूट करने में विफल: `{e}`")


@Client.on_message(filters.command("unmute") & filters.group)
async def unmute_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ जिस यूज़र को अनम्यूट करना है, उसके मैसेज पर रिप्लाई करें!")
    target_user = message.reply_to_message.from_user
    try:
        await client.restrict_chat_member(
            message.chat.id, target_user.id,
            ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
        )
        await message.reply_text(f"🔊 **{target_user.mention} को अनम्यूट कर दिया गया है।**")
    except Exception as e:
        await message.reply_text(f"❌ अनम्यूट करने में विफल: `{e}`")


@Client.on_message(filters.command("leavegrp") & filters.group)
async def leave_group_cmd(client: Client, message: Message):
    await message.reply_text("👋 **बाय बाय! बॉट इस ग्रुप को छोड़ रहा है...**")
    await client.leave_chat(message.chat.id)


@Client.on_message(filters.command("auth"))
async def auth_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ रिप्लाई करें!")
    user_id = message.reply_to_message.from_user.id
    AUTHORIZED_USERS.add(user_id)
    await message.reply_text(f"🔑 **यूज़र (`{user_id}`) ऑथराइज़्ड हो गया!**")


@Client.on_message(filters.command("rem_auth"))
async def rem_auth_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ रिप्लाई करें!")
    user_id = message.reply_to_message.from_user.id
    AUTHORIZED_USERS.discard(user_id)
    await message.reply_text(f"🧹 **यूज़र (`{user_id}`) का एक्सेस हटा दिया गया!**")


@Client.on_message(filters.command("banlist"))
async def banlist_cmd(client: Client, message: Message):
    if not BANNED_USERS:
        return await message.reply_text("📄 **बैन लिस्ट खाली है।**")
    ban_text = "📄 **बैन यूज़र्स:**\n\n" + "\n".join([f"• `{uid}`" for uid in BANNED_USERS])
    await message.reply_text(ban_text)
    
