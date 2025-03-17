from pyrogram import Client
from config import API_ID, API_HASH, SESSION_STRINGS

clients = []

for session in SESSION_STRINGS:
    try:
        client = Client(
            session_string=session,
            api_id=API_ID,
            api_hash=API_HASH,
            in_memory=True
        )
        clients.append(client)
    except Exception as e:
        print(f"[!] Error loading session: {e}")
