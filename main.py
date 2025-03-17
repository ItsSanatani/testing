from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import InputReportReasonSpam, InputReportReasonViolence, InputReportReasonPornography, InputReportReasonChildAbuse, InputReportReasonOther
import logging
from config import BOT_TOKEN, API_ID, API_HASH, SESSION_STRINGS, REPORT_COUNT, REPORT_REASON

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot client initialization
bot = Client("mass_report_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# User clients initialization
user_clients = []
for session_string in SESSION_STRINGS:
    user_clients.append(Client(session_string, api_id=API_ID, api_hash=API_HASH))

# Start all user clients
for user_client in user_clients:
    user_client.start()

# Mapping report reasons to Pyrogram's raw types
REPORT_REASONS = {
    "spam": InputReportReasonSpam,
    "violence": InputReportReasonViolence,
    "pornography": InputReportReasonPornography,
    "child_abuse": InputReportReasonChildAbuse,
    "other": InputReportReasonOther
}

@bot.on_message(filters.command("report") & filters.private)
async def report_handler(bot_client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: `/report <username or group link or message link>`", quote=True)
        return

    target = message.command[1]

    if target.startswith("https://t.me/"):
        # Handle message link
        parts = target.split("/")
        if len(parts) >= 5 and parts[-2].isdigit() and parts[-1].isdigit():
            chat_id = int("-100" + parts[-2])
            message_id = int(parts[-1])
            success_count, failure_count = await mass_report_message(chat_id, message_id)
            await message.reply_text(f"Message {message_id} in chat {chat_id} reported by all sessions.\nSuccessful: {success_count}, Failed: {failure_count}")
        else:
            await message.reply_text("Invalid message link format.", quote=True)
    elif target.startswith("@"):
        # Handle username or group link
        success_count, failure_count = await mass_report_entity(target)
        await message.reply_text(f"{target} reported by all sessions.\nSuccessful: {success_count}, Failed: {failure_count}")
    else:
        await message.reply_text("Invalid target format. Use a username, group link, or message link.", quote=True)

async def mass_report_entity(entity):
    success_count = 0
    failure_count = 0
    reason_class = REPORT_REASONS.get(REPORT_REASON, InputReportReasonOther)
    reason_instance = reason_class()
    for user_client in user_clients:
        for _ in range(REPORT_COUNT):
            try:
                peer = await user_client.resolve_peer(entity)
                await user_client.invoke(ReportPeer(peer=peer, reason=reason_instance, message="Inappropriate content"))
                logger.info(f"{entity} reported by session {user_client.session_name}")
                success_count += 1
            except RPCError as e:
                logger.error(f"Failed to report {entity} by session {user_client.session_name}: {e}")
                failure_count += 1
    return success_count, failure_count

async def mass_report_message(chat_id, message_id):
    success_count = 0
    failure_count = 0
    reason_class = REPORT_REASONS.get(REPORT_REASON, InputReportReasonOther)
    reason_instance = reason_class()
    for user_client in user_clients:
        for _ in range(REPORT_COUNT):
            try:
                peer = await user_client.resolve_peer(chat_id)
                await user_client.invoke(ReportPeer(peer=peer, reason=reason_instance, message="Inappropriate message"))
                logger.info(f"Message {message_id} in chat {chat_id} reported by session {user_client.session_name}")
                success_count += 1
            except RPCError as e:
                logger.error(f"Failed to report message {message_id} in chat {chat_id} by session {user_client.session_name}: {e}")
                failure_count += 1
    return success_count, failure_count

if __name__ == "__main__":
    bot.run()
