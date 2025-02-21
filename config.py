import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///podcast_bot.db')
    EPISODES_DIR = os.path.join('llm', 'episodes')

    @staticmethod
    def init_app(app):
        # Create necessary directories
        os.makedirs(Config.EPISODES_DIR, exist_ok=True) 