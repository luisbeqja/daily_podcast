import os
from dotenv import load_dotenv

# Only load .env file if not in production
if not os.getenv('RAILWAY_ENVIRONMENT'):
    load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Use Railway's PostgreSQL URL if available
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///podcast_bot.db')
    
    # Use Railway's persistent storage path if available
    STORAGE_PATH = os.getenv('RAILWAY_VOLUME_MOUNT_PATH', '')
    EPISODES_DIR = os.path.join(STORAGE_PATH, 'llm', 'episodes')

    @staticmethod
    def init_app(app):
        # Create necessary directories
        os.makedirs(Config.EPISODES_DIR, exist_ok=True) 