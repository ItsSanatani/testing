# main.py

from pyrogram import Client, filters
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import (
    InputReportReasonSpam,
    InputReportReasonViolence,
    InputReportReasonPornography,
    InputReportReasonChildAbuse,
    InputReportReasonCopyright,
    InputReportReasonIllegalDrugs,
    InputReportReasonPersonalDetails,
    InputReportReasonGeoIrrelevant,
    InputReportReasonOther
)
from config import BOT_TOKEN, API_ID, API_HASH
from client_sessions import clients
import asyncio

# Mapping reasons
REASONS = {
    "1": InputReportReasonSpam,
    "2": InputReportReasonChildAbuse,
    "3": InputReportReasonViolence,
    "4": InputReportReasonIllegalDrugs,
    "5": InputReportReasonPornography,
    "6": InputReportReasonPersonalDetails,
    "7": InputReportReasonGeoIrrelevant,
    "8": InputReportReasonSpam,
    "9": InputReportReasonCopyright,
    "10": InputReportReasonOther,
    "11": InputReportReasonOther
}

bot = Client("report_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)


@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    await message.reply_text(
        "**Welcome to Mass Report Bot!**\n\n"
        "**Please send me in following format:**\n"
        "`Group Link`\n"
        "`Message Link (optional)`\n"
        "`Report Reason (number)`\n"
        "`Report Count`\n\n"
        "**Available Reasons:**\n"
        "1. I don't like it (Spam)\n"
        "2. Child Abuse\n"
        "3. Violence\n"
        "4. Illegal Goods\n"
        "5. Illegal Adult Content\n"
        "6. Personal Data\n"
        "7. Terrorism\n"
        "8. Scam or Spam\n"
        "9. Copyright\n"
        "10. Other\n"
        "11. It's not illegal but must be taken down"
    )


@bot.on_message(filters.private & filters.text)
async def report_handler(client, message):
    try:
        lines = message.text.split('\n')
        if len(lines) < 4:
            await message.reply_text("Please send all details correctly as instructed!")
            return

        group_link = lines[0].strip()
        message_link = lines[1].strip()
        reason_num = lines[2].strip()
        count = int(lines[3].strip())

        if reason_num not in REASONS:
            await message.reply_text("Invalid reason number!")
            return

        reason = REASONS[reason_num]()
        success, failed = 0, 0

        await message.reply_text("Starting mass report...")

        for i in range(count):
            for session_client in clients:
                try:
                    await session_client.start()
                    peer = await session_client.resolve_peer(group_link)
                    await session_client.invoke(ReportPeer(peer=peer, reason=reason, message="Reported"))
                    await session_client.stop()
                    success += 1
                except Exception as e:
                    failed += 1
                    continue
            await asyncio.sleep(1)  # avoid flood

        await message.reply_text(
            f"✅ Mass Reporting Completed!\n\n"
            f"Successful Reports: {success}\n"
            f"Failed Reports: {failed}"
        )

    except Exception as e:
        await message.reply_text(f"Error: {e}")


bot.run()
