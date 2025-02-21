import sqlite3
import os
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_file=None):
        if Config.DATABASE_URL.startswith('postgres://'):
            self.db_file = Config.DATABASE_URL
        else:
            self.db_file = db_file or os.path.join(Config.STORAGE_PATH, 'podcast_bot.db')
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

    def clear_user_data(self, user_id: int):
        """Clear all podcasts for a specific user."""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        try:
            # Get paths to delete
            c.execute('SELECT intro_path, episode_path FROM podcasts WHERE user_id = ?', (user_id,))
            paths = c.fetchall()
            
            # Delete from database
            c.execute('DELETE FROM podcasts WHERE user_id = ?', (user_id,))
            conn.commit()
            
            # Delete files
            for intro_path, episode_path in paths:
                try:
                    if intro_path and os.path.exists(intro_path):
                        os.remove(intro_path)
                    if episode_path and os.path.exists(episode_path):
                        os.remove(episode_path)
                except Exception as e:
                    logger.error(f"Error deleting files: {e}")
                
            return True
        except Exception as e:
            logger.error(f"Error clearing user data: {e}")
            return False
        finally:
            conn.close() 

    def get_all_users(self):
        """Get all users and their podcast count."""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        try:
            c.execute('''
                SELECT 
                    u.user_id,
                    u.username,
                    u.created_at,
                    COUNT(p.id) as podcast_count
                FROM users u
                LEFT JOIN podcasts p ON u.user_id = p.user_id
                GROUP BY u.user_id
                ORDER BY u.created_at DESC
            ''')
            
            users = []
            for user_id, username, created_at, podcast_count in c.fetchall():
                users.append({
                    "user_id": user_id,
                    "username": username,
                    "created_at": created_at,
                    "podcast_count": podcast_count
                })
            
            return users
        finally:
            conn.close()

    def get_stats(self):
        """Get general statistics about the bot usage."""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        try:
            stats = {}
            
            # Get total users
            c.execute('SELECT COUNT(*) FROM users')
            stats['total_users'] = c.fetchone()[0]
            
            # Get total podcasts
            c.execute('SELECT COUNT(*) FROM podcasts')
            stats['total_podcasts'] = c.fetchone()[0]
            
            # Get podcasts by language
            c.execute('''
                SELECT language, COUNT(*) as count
                FROM podcasts
                GROUP BY language
            ''')
            stats['podcasts_by_language'] = {
                lang: count for lang, count in c.fetchall()
            }
            
            # Get podcasts created today
            c.execute('''
                SELECT COUNT(*) 
                FROM podcasts 
                WHERE date(created_at) = date('now')
            ''')
            stats['podcasts_today'] = c.fetchone()[0]
            
            return stats
        finally:
            conn.close() 