from pyrogram import Client
from config import API_ID, API_HASH, SESSION_STRINGS

clients = []

for i, session in enumerate(SESSION_STRINGS, start=1):
    try:
        client = Client(
            name=f"client{i}",  # koi bhi unique name de sakte ho
            session_string=session,
            api_id=API_ID,
            api_hash=API_HASH,
            in_memory=True
        )
        clients.append(client)
    except Exception as e:
        print(f"[!] Error loading session: {e}")
