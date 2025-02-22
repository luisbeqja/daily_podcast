import os
import logging
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    podcasts = relationship("Podcast", back_populates="user")

class Podcast(Base):
    __tablename__ = 'podcasts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    topic = Column(String)
    language = Column(String)
    intro_path = Column(String)
    episode_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="podcasts")

class Database:
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables."""
        try:
            Base.metadata.create_all(self.engine)
            # Test the connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("✅ Database connected successfully!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            logger.error(f"Error initializing database: {e}")
            raise

    def add_user(self, user_id: int, username: str = None):
        """Add a new user to the database."""
        session = self.Session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                user = User(user_id=user_id, username=username)
                session.add(user)
                session.commit()
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            session.rollback()
        finally:
            session.close()

    def add_podcast(self, user_id: int, topic: str, language: str, intro_path: str, episode_path: str):
        """Add a new podcast to the database."""
        session = self.Session()
        try:
            podcast = Podcast(
                user_id=user_id,
                topic=topic,
                language=language,
                intro_path=intro_path,
                episode_path=episode_path
            )
            session.add(podcast)
            session.commit()
        except Exception as e:
            logger.error(f"Error adding podcast: {e}")
            session.rollback()
        finally:
            session.close()

    def get_user_podcasts(self, user_id: int):
        """Get all podcasts for a specific user."""
        session = self.Session()
        try:
            podcasts = session.query(Podcast).filter_by(user_id=user_id).order_by(Podcast.created_at.desc()).all()
            return [(p.topic, p.language, p.intro_path, p.episode_path, p.created_at) for p in podcasts]
        finally:
            session.close()

    def user_exists(self, user_id: int):
        """Check if a user exists in the database."""
        session = self.Session()
        try:
            return session.query(User).filter_by(user_id=user_id).first() is not None
        finally:
            session.close()

    def clear_user_data(self, user_id: int):
        """Clear all podcasts for a specific user."""
        session = self.Session()
        try:
            podcasts = session.query(Podcast).filter_by(user_id=user_id).all()
            
            # Delete files
            for podcast in podcasts:
                try:
                    if podcast.intro_path and os.path.exists(podcast.intro_path):
                        os.remove(podcast.intro_path)
                    if podcast.episode_path and os.path.exists(podcast.episode_path):
                        os.remove(podcast.episode_path)
                except Exception as e:
                    logger.error(f"Error deleting files: {e}")
            
            # Delete database records
            session.query(Podcast).filter_by(user_id=user_id).delete()
            session.commit()
            return True
        except Exception as e:
            logger.error(f"Error clearing user data: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_all_users(self):
        """Get all users and their podcast count."""
        session = self.Session()
        try:
            users = session.query(User).all()
            return [{
                "user_id": user.user_id,
                "username": user.username,
                "created_at": user.created_at,
                "podcast_count": len(user.podcasts)
            } for user in users]
        finally:
            session.close()

    def get_stats(self):
        """Get general statistics about the bot usage."""
        session = self.Session()
        try:
            stats = {}
            
            # Get total users
            stats['total_users'] = session.query(User).count()
            
            # Get total podcasts
            stats['total_podcasts'] = session.query(Podcast).count()
            
            # Get podcasts by language
            language_counts = session.query(
                Podcast.language, 
                text('COUNT(*) as count')
            ).group_by(Podcast.language).all()
            stats['podcasts_by_language'] = {
                lang: count for lang, count in language_counts
            }
            
            # Get podcasts created today
            today_count = session.query(Podcast).filter(
                text("DATE(created_at) = CURRENT_DATE")
            ).count()
            stats['podcasts_today'] = today_count
            
            return stats
        finally:
            session.close() 