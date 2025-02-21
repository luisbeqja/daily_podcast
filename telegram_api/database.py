import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_file="podcast_bot.db"):
        self.db_file = db_file
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create podcasts table
        c.execute('''
            CREATE TABLE IF NOT EXISTS podcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                topic TEXT,
                language TEXT,
                intro_path TEXT,
                episode_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_user(self, user_id: int, username: str = None):
        """Add a new user to the database."""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)',
                 (user_id, username))
        
        conn.commit()
        conn.close()

    def add_podcast(self, user_id: int, topic: str, language: str, intro_path: str, episode_path: str):
        """Add a new podcast to the database."""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO podcasts (user_id, topic, language, intro_path, episode_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, topic, language, intro_path, episode_path))
        
        conn.commit()
        conn.close()

    def get_user_podcasts(self, user_id: int):
        """Get all podcasts for a specific user."""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute('''
            SELECT topic, language, intro_path, episode_path, created_at
            FROM podcasts
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        podcasts = c.fetchall()
        conn.close()
        
        return podcasts

    def user_exists(self, user_id: int):
        """Check if a user exists in the database."""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        exists = c.fetchone() is not None
        
        conn.close()
        return exists 