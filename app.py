from flask import Flask, jsonify, request
import threading
from telegram_api.bot import start_bot
from config import Config
import os

from llm.llm import create_episode, create_episode_lineup, create_first_episode

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Global variable to track the bot thread
bot_thread = None

def ensure_bot_running():
    """Ensure the bot is running in a separate thread."""
    global bot_thread
    if bot_thread is None or not bot_thread.is_alive():
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        return True
    return False

@app.route('/')
def home():
    return jsonify({"status": "Bot is running"}), 200

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    start_bot()  # Start the bot first
    app.run(host='0.0.0.0', port=port)
