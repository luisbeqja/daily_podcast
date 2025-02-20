from llm.config import logger, openai
from llm.text_to_speech import text_to_speech



def create_episode_lineup(message):
    """Send a message to OpenAI and return the response."""
    try:
        completion = openai.chat.completions.create(
        model="gpt-4o-mini",  # Updated model name
        messages=[
                {"role": "system", "content": """
                 You are an podcaster assistant your name is "Lisa". 
                 For now you have to create an episode lineup for the podcast.
                 The episode lineup should be in 5 episodes.
                 The episode lineup should be in the following format:
                 Title of the podcast: Title of the podcast
                 Episode 1: Topic of the episode in short
                 Episode 2: Topic of the episode in short
                 ...
                 Episode 5: Topic of the episode in short
                 return only the episode lineup, no other text.
                 """},
                {"role": "user", "content": f"this is prompt of the user for the episode lineup: {message}"},
            ]
        )
        text_to_speech(completion.choices[0].message.content, "first_episode")
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise


def create_first_episode(message, episode_lineup):
    """Send a message to OpenAI and return the response."""
    try:
        completion = openai.chat.completions.create(
        model="gpt-4o-mini",  # Updated model name
        messages=[
                {"role": "system", "content": """
                 You are an podcaster assistant your name is "Lisa". 
                 For now you have only to write a script for the intro intro of the podcast. 
                 The script should be in 30 seconds long.
                 The script should explain the main topic of the podcast.
                 Explain how the episode lineup is going to be.
                 Remember the script, is then going to be read by a Text to Speech model by OpenAI with voice alloy.
                 """},
                {"role": "user", "content": f"this is the episode lineup: {episode_lineup} and the topic of the podcast: {message}"},
            ]
        )
        text_to_speech(completion.choices[0].message.content, "first_episode")
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise

def create_episode(message, episode_number, previous_episode_script):
    """Send a message to OpenAI and return the response."""
    try:
        completion = openai.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
                {"role": "system", "content": f"""
                 You are an podcaster assistant your name is "Lisa". 
                 You to write the script for the episode {episode_number} of the podcast. 
                 The script should be in 3 minutes long.
                 this is the script of the previous episode: {previous_episode_script}
                 
                 Remember the script, is then going to be read by a Text to Speech model by OpenAI with voice alloy.
                 the output should be MAX 4000 characters.
                 """},
                {"role": "user", "content": f"this is prompt of the user for the first episode: {message}"},
            ]
        )
        text_to_speech(completion.choices[0].message.content, f"episode_{episode_number}")
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise
