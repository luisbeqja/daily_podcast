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
    # Run bot using asyncio.run() to avoid deprecation warning
    asyncio.run(start_bot())
