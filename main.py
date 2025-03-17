import asyncio
from pyrogram import Client, filters, errors
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
from helpers import extract_username

# Reporting reasons ka mapping
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
        "**Please send me the following details in this format:**\n"
        "`Group Link`\n"
        "`Message Link (optional)`\n"
        "`Report Reason (number)`\n"
        "`Report Count`\n\n"
        "**Available Reasons:**\n"
        "1. Spam\n"
        "2. Child Abuse\n"
        "3. Violence\n"
        "4. Illegal Drugs\n"
        "5. Pornography\n"
        "6. Personal Details\n"
        "7. Geo Irrelevant\n"
        "8. Spam\n"
        "9. Copyright\n"
        "10. Other\n"
        "11. Other"
    )

@bot.on_message(filters.private & filters.text)
async def report_handler(client, message):
    try:
        lines = message.text.split('\n')
        if len(lines) < 4:
            await message.reply_text("Please send all details correctly as instructed!")
            return

        group_link = lines[0].strip()
        message_link = lines[1].strip() if len(lines) > 1 else None
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
                    username = extract_username(group_link)

                    # Resolve Peer
                    peer = await session_client.resolve_peer(username)

                    if message_link:
                        # Message ID extract karo
                        msg_id = int(message_link.split("/")[-1])
                        await session_client.invoke(
                            ReportPeer(
                                peer=peer,
                                reason=reason,
                                message="Reported"
                            )
                        )
                    else:
                        await session_client.invoke(
                            ReportPeer(
                                peer=peer,
                                reason=reason,
                                message="Reported"
                            )
                        )
                    success += 1

                except errors.FloodWait as e:
                    await asyncio.sleep(e.value)
                    failed += 1
                except Exception as e:
                    print(f"Error: {e}")
                    failed += 1
                finally:
                    await session_client.stop()
            await asyncio.sleep(1)  # avoid flood

        await message.reply_text(
            f"✅ Mass Reporting Completed!\n\n"
            f"Successful Reports: {success}\n"
            f"Failed Reports: {failed}"
        )

    except Exception as e:
        await message.reply_text(f"Error: {e}")

bot.run()
