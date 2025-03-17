from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import InputReportReasonChildAbuse
from telethon.tl.functions.messages import ImportChatInviteRequest

from pyrogram import Client, filters
import asyncio
import config

# Bot client (Pyrogram)
bot = Client("mass_report_bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)

# Function to handle reporting from a single session
async def report_from_session(session_string, target_link):
    try:
        client = TelegramClient(StringSession(session_string), config.API_ID, config.API_HASH)
        await client.start()
        me = await client.get_me()
        print(f"[+] Logged in as: {me.username or me.id}")
        
        if "t.me/+" in target_link:  # Private group invite link
            invite_hash = target_link.split("+")[-1]
            await client(ImportChatInviteRequest(invite_hash))
            print(f"[+] Joined private group via invite link: {target_link}")
            print(f"[!] Cannot directly report a message via invite link. Please provide message link or username.")

        elif "/c/" in target_link:  # Private group message link
            parts = target_link.split('/')
            chat_id = int("-100" + parts[-2])
            await client(ReportPeerRequest(
                peer=chat_id,
                reason=InputReportReasonChildAbuse(),
                message="Child abuse content"
            ))
            print(f"[+] Reported private group: {target_link}")

        else:  # Public username or group
            parts = target_link.split('/')
            username = parts[-2].replace('@', '')
            entity = await client.get_entity(username)
            await client(ReportPeerRequest(
                peer=entity,
                reason=InputReportReasonChildAbuse(),
                message="Child abuse content"
            ))
            print(f"[+] Reported public group/user: {target_link}")

        await client.disconnect()

    except Exception as e:
        print(f"[!] Error in session: {e}")

# Bot command handler
@bot.on_message(filters.command("report") & filters.private)
async def report_handler(_, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: `/report <username or group link>`", quote=True)
        return
    
    target_link = message.command[1]
    await message.reply_text(f"Mass reporting `{target_link}` from all sessions...")

    # Launch reporting from all sessions
    tasks = []
    for session in config.SESSION_STRINGS:
        tasks.append(report_from_session(session, target_link))
    
    await asyncio.gather(*tasks)
    await message.reply_text("✅ Reporting completed from all sessions.")

# Start bot
bot.run()
