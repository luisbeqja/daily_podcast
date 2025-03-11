from llm.config import logger, openai
from llm.text_to_speech import ElevenLabsTextToSpeech
from llm.prompts.prompt_loader import LANGUAGE_PROMPTS, EPISODE_LINEUP_PROMPT, FIRST_EPISODE_PROMPT, EPISODE_PROMPT
import os

def ensure_user_directory(user_id):
    """Create a directory for the user if it doesn't exist."""
    user_dir = os.path.join("llm", "episodes", str(user_id))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return user_dir

def create_episode_lineup(message, language, user_id):
    """Send a message to OpenAI and return the response."""
    print(f"Creating episode lineup for user {user_id} in {language}")
    try:
        lang_instruction = LANGUAGE_PROMPTS.get(language, LANGUAGE_PROMPTS['en'])
        system_prompt = EPISODE_LINEUP_PROMPT.format(language_instruction=lang_instruction)
        
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",  # Updated model name
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a podcast lineup about: {message}"},
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise

def create_first_episode(message, episode_lineup, language, user_id):
    """Send a message to OpenAI and return the response."""
    try:
        lang_instruction = LANGUAGE_PROMPTS.get(language, LANGUAGE_PROMPTS['en'])
        system_prompt = FIRST_EPISODE_PROMPT.format(language_instruction=lang_instruction)
        
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""
                 Create an intro for a podcast about: {message}\nThis is the episode lineup: {episode_lineup}
                 Use the Speech Synthesis Markup Language(SSML) to add pauses and emphasis to the text.
                 make it <emphasis level="moderate">....</emphasis> and <prosody rate="slow">...</prosody>
                 """},
            ]
        )
        
        # Create user directory and save file there
        user_dir = ensure_user_directory(user_id)
        ElevenLabsTextToSpeech(completion.choices[0].message.content, os.path.join(user_dir, "first_episode"))
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise

def create_episode(message, episode_number, previous_episode_script, episode_lineup, language, user_id):
    """Send a message to OpenAI and return the response."""
    try:
        lang_instruction = LANGUAGE_PROMPTS.get(language, LANGUAGE_PROMPTS['en'])
        system_prompt = EPISODE_PROMPT.format(
            episode_number=episode_number,
            episode_lineup=episode_lineup,
            previous_episode_script=previous_episode_script,
            language_instruction=lang_instruction
        )
        
        completion = openai.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""
                    Create episode {episode_number} about: {message}
                    Use the Speech Synthesis Markup Language(SSML) to add pauses and emphasis to the text.
                    make it <emphasis level="moderate">....</emphasis> and <prosody rate="slow">...</prosody>
                 """},
            ]
        )
        # Create user directory and save file there
        user_dir = ensure_user_directory(user_id)
        ElevenLabsTextToSpeech(completion.choices[0].message.content, os.path.join(user_dir, f"episode_{episode_number}"))
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise

def start_initial_chain(message, language, user_id, db):
    """Start the chain of the podcast."""
    print(f"Starting initial chain for user {user_id}")
    
    user_dir = os.path.join("llm", "episodes", str(user_id))
    intro_path = os.path.join(user_dir, "first_episode.mp3")
    episode_path = os.path.join(user_dir, "episode_1.mp3")
    
    episode_lineup = create_episode_lineup(message, language, user_id)
    first_episode = create_first_episode(message, episode_lineup, language, user_id)
    episode_1 = create_episode(message, 1, first_episode, episode_lineup, language, user_id)
    
    # Save podcast information to database with user-specific paths        
    db.add_podcast(
        user_id=user_id,
        topic=message,
        language=language,
        intro_path=intro_path,
        episode_path=episode_path,
        episode_lineup=episode_lineup,
        episode_content=episode_1
    )
    
    return episode_1

def start_chain(message, language, user_id, db, episode_number):
    """Start the chain of the podcast."""
    print(f"Starting chain for user {user_id}")
    
    user_dir = os.path.join("llm", "episodes", str(user_id))
    episode_path = os.path.join(user_dir, f"episode_{episode_number}.mp3")
    
    episode_lineup = db.get_user_lineup(user_id)
    print(f"Episode lineup: {episode_lineup}")

    episode = create_episode(message, episode_number, (db.get_user_podcast_episode(user_id) or ""), episode_lineup, language, user_id)
    
    episode_content = f"{(db.get_user_podcast_episode(user_id) or 'No previous episode')} \n\n {episode}"
    
    # Save podcast information to database with user-specific paths    
    db.update_podcast(
        user_id=user_id,
        episode_path=episode_path,
        episode_content=episode_content
    )
    return episode_content
    
    
