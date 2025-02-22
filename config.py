import os
from dotenv import load_dotenv

# Only load .env file if not in production
if not os.getenv('RAILWAY_ENVIRONMENT'):
    load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Get PostgreSQL URL from Railway or use default SQLite
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        # Convert postgres:// to postgresql:// for SQLAlchemy
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    else:
        DATABASE_URL = 'sqlite:///podcast_bot.db'
    
    # Use Railway's persistent storage path if available
    STORAGE_PATH = os.getenv('RAILWAY_VOLUME_MOUNT_PATH', '')
    EPISODES_DIR = os.path.join(STORAGE_PATH, 'llm', 'episodes')

    @staticmethod
    def init_app(app):
        # Create necessary directories
        os.makedirs(Config.EPISODES_DIR, exist_ok=True) 