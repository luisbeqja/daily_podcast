import os
import logging
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(BigInteger, primary_key=True)
    username = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    podcasts = relationship("Podcast", back_populates="user")

class Podcast(Base):
    __tablename__ = 'podcasts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    topic = Column(String)
    language = Column(String)
    intro_path = Column(String)
    episode_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="podcasts")
    episode_lineup = Column(String)
    episode_content = Column(String)

class Database:
    def __init__(self):
        """Initialize database connection."""
        try:
            # Use the database URL from Config instead of directly from environment
            database_url = Config.DATABASE_URL
            
            logger.info(f"Connecting to database: {database_url}")
            
            self.engine = create_engine(database_url)
            self.Session = sessionmaker(bind=self.engine)
            
            # Create all tables
            self.init_db()
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def init_db(self):
        """Initialize database tables."""
        try:
            # Drop existing tables if they exist
            Base.metadata.drop_all(self.engine)
            # Create new tables with updated schema
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
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

    def add_podcast(self, user_id: int, topic: str, language: str, intro_path: str, episode_path: str, episode_lineup: str, episode_content: str):
        """Add a new podcast to the database."""
        session = self.Session()
        try:
            podcast = Podcast(
                user_id=user_id,
                topic=topic,
                language=language,
                intro_path=intro_path,
                episode_path=episode_path,
                episode_lineup=episode_lineup,
                episode_content=episode_content
            )
            session.add(podcast)
            session.commit()
        except Exception as e:
            logger.error(f"Error adding podcast: {e}")
            session.rollback()
        finally:
            session.close()
            
    def update_podcast(self, user_id: int,episode_path: str, episode_content: str):
        """Update a podcast in the database."""
        session = self.Session()
        try:
            podcast = session.query(Podcast).filter_by(user_id=user_id).first()
            if podcast:
                podcast.topic = podcast.topic
                podcast.language = podcast.language
                podcast.intro_path = podcast.intro_path
                podcast.episode_path = episode_path
                podcast.episode_lineup = podcast.episode_lineup
                podcast.episode_content = episode_content
                session.commit()
        except Exception as e:
            logger.error(f"Error updating podcast: {e}")
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

    def get_user_podcast_episode(self, user_id: int):
        """Get the latest episode for a specific user."""
        session = self.Session()
        try:
            podcast = session.query(Podcast).filter_by(user_id=user_id).order_by(Podcast.created_at.desc()).first()
            return podcast.episode_content
        finally:
            session.close()
    
    def get_user_lineup(self, user_id: int):
        """Get the lineup for a specific user."""
        session = self.Session()
        try:
            podcast = session.query(Podcast).filter_by(user_id=user_id).order_by(Podcast.created_at.desc()).first()
            return podcast.episode_lineup
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