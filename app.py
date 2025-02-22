import asyncio
from telegram_api.bot import start_bot
from telegram_api.database import Database
from config import Config

# Initialize database
try:
    db = Database()
    print(f"🔌 Connected to database at: {Config.DATABASE_URL}")
except Exception as e:
    print(f"❌ Failed to connect to database: {e}")
    raise

if __name__ == '__main__':
    # Run bot in main thread
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
    loop.run_forever()
