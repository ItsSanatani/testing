import asyncio
from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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
from client_sessions import clients  # List of Client sessions
from helpers import extract_username

user_data = {}  # State management for each user

REASON_MAP = {
    "1": ("Spam", InputReportReasonSpam),
    "2": ("Child Abuse", InputReportReasonChildAbuse),
    "3": ("Violence", InputReportReasonViolence),
    "4": ("Illegal Drugs", InputReportReasonIllegalDrugs),
    "5": ("Pornography", InputReportReasonPornography),
    "6": ("Personal Details", InputReportReasonPersonalDetails),
    "7": ("Geo Irrelevant", InputReportReasonGeoIrrelevant),
    "8": ("Copyright", InputReportReasonCopyright),
    "9": ("Other", InputReportReasonOther)
}

bot = Client("mass_report_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# /start command
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_data[message.from_user.id] = {}
    await message.reply_text(
        "**Welcome to Mass Report Bot!**\n\n"
        "Please send me the **Target Group/Channel Link**:"
    )

# Handle all steps
@bot.on_message(filters.private & filters.text)
async def handle_steps(client, message):
    user_id = message.from_user.id
    data = user_data.get(user_id, {})

    # Step 1: Get Target Link
    if "target" not in data:
        data["target"] = message.text.strip()
        user_data[user_id] = data
        await message.reply_text("Now send me the **Message Link** (Target Message to report):")
        return

    # Step 2: Get Message Link
    if "message_link" not in data:
        data["message_link"] = message.text.strip()
        user_data[user_id] = data

        # Ask for reason
        buttons = [
            [InlineKeyboardButton(f"{key}. {val[0]}", callback_data=f"reason_{key}")]
            for key, val in REASON_MAP.items()
        ]
        await message.reply_text(
            "**Select Report Reason:**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # Step 3: Get Count
    if "reason" in data and "count" not in data:
        try:
            count = int(message.text.strip())
            data["count"] = count
            user_data[user_id] = data
            await message.reply_text(f"**Starting Mass Report...**")
            await start_reporting(client, message, data)
        except ValueError:
            await message.reply_text("Please send a valid number for count!")
        return

# Handle Reason Selection
@bot.on_callback_query(filters.regex(r"reason_\d+"))
async def reason_selected(client, callback_query):
    user_id = callback_query.from_user.id
    reason_num = callback_query.data.split("_")[1]
    reason_tuple = REASON_MAP.get(reason_num)

    if not reason_tuple:
        await callback_query.answer("Invalid Reason!", show_alert=True)
        return

    user_data[user_id]["reason"] = reason_tuple[1]
    await callback_query.message.edit_text(f"Selected Reason: **{reason_tuple[0]}**\n\nNow send me **Report Count**:")

# Reporting Function
async def start_reporting(client, message, data):
    target_link = data["target"]
    message_link = data["message_link"]
    reason = data["reason"]()
    count = data["count"]

    username = extract_username(target_link)
    msg_id = int(message_link.split("/")[-1])

    success, failed = 0, 0

    for i in range(count):
        for session_client in clients:
            try:
                await session_client.start()

                # Join target group/channel
                try:
                    await session_client.join_chat(username)
                except errors.UserAlreadyParticipant:
                    pass
                except Exception as e:
                    print(f"Join Error: {e}")

                # Resolve peer
                peer = await session_client.resolve_peer(username)

                # Report
                await session_client.invoke(
                    ReportPeer(
                        peer=peer,
                        reason=reason,
                        message=f"Reported message {msg_id}"
                    )
                )
                success += 1

            except errors.FloodWait as e:
                print(f"FloodWait: Sleeping {e.value} seconds")
                await asyncio.sleep(e.value)
                failed += 1
            except Exception as e:
                print(f"Error: {e}")
                failed += 1
            finally:
                await session_client.stop()
        await asyncio.sleep(1)  # Little delay

    await message.reply_text(
        f"✅ **Mass Reporting Completed!**\n\n"
        f"**Successful Reports:** {success}\n"
        f"**Failed Reports:** {failed}"
    )
    # Clean user data
    user_data.pop(message.from_user.id, None)

bot.run()
