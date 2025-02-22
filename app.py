from flask import Flask, jsonify, request
import threading
import asyncio
from telegram_api.bot import start_bot
from telegram_api.database import Database
from config import Config
import os
from datetime import datetime

from llm.llm import create_episode, create_episode_lineup, create_first_episode

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Initialize database
try:
    db = Database()
    print(f"🔌 Connected to database at: {Config.DATABASE_URL}")
except Exception as e:
    print(f"❌ Failed to connect to database: {e}")
    raise

# Global variable for bot thread
bot_thread = None

def run_bot():
    """Run the bot with its own event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

def start_bot_thread():
    global bot_thread
    if bot_thread is None or not bot_thread.is_alive():
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()

# Start bot thread immediately
start_bot_thread()

@app.route('/')
def home():
    return jsonify({"status": "Bot is running"}), 200

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/users')
def get_users():
    """Get all users and their podcast count."""
    try:
        users = db.get_all_users()
        return jsonify({
            "status": "success",
            "users": users
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/podcasts/<int:user_id>')
def get_user_podcasts(user_id):
    """Get all podcasts for a specific user."""
    try:
        podcasts = db.get_user_podcasts(user_id)
        if not podcasts:
            return jsonify({
                "status": "not_found",
                "message": "No podcasts found for this user"
            }), 404
            
        formatted_podcasts = []
        for topic, language, intro_path, episode_path, created_at in podcasts:
            formatted_podcasts.append({
                "topic": topic,
                "language": language,
                "created_at": created_at,
                "has_intro": bool(intro_path and os.path.exists(intro_path)),
                "has_episode": bool(episode_path and os.path.exists(episode_path))
            })
            
        return jsonify({
            "status": "success",
            "podcasts": formatted_podcasts
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """Get general statistics about the bot usage."""
    try:
        stats = db.get_stats()
        return jsonify({
            "status": "success",
            "stats": stats
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
