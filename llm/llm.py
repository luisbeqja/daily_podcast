from llm.config import logger, openai
from llm.text_to_speech import text_to_speech

language_prompts = {
        'en': "Create the response in English",
        'es': "Crea la respuesta en español. Asegúrate que todo el texto esté en español.",
        'it': "Crea la risposta in italiano. Assicurati che tutto il testo sia in italiano."
}
        

def create_episode_lineup(message, language):
    """Send a message to OpenAI and return the response."""
    print("Creating episode lineup" + language)
    try:
        lang_instruction = language_prompts.get(language, language_prompts['en'])
        
        completion = openai.chat.completions.create(
        model="gpt-4o-mini",  # Updated model name
        messages=[
                {"role": "system", "content": f"""
                 You are an podcaster assistant your name is "Lisa". 
                 For now you have to create an episode lineup for the podcast.
                 The episode lineup should be in 5 episodes.
                 The episode lineup should be in the following format:
                 
                 Title of the podcast: Title of the podcast
                 Episode 1: Topic of the episode in short
                 Episode 2: Topic of the episode in short
                 ...
                 Episode 5: Topic of the episode in short
                 
                 {lang_instruction}
                 return only the episode lineup, no other text.
                 """},
                {"role": "user", "content": f"Create a podcast lineup about: {message}"},
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise


def create_first_episode(message, episode_lineup, language):
    """Send a message to OpenAI and return the response."""
    try:
        lang_instruction = language_prompts.get(language, language_prompts['en'])
        
        completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {"role": "system", "content": f"""
                 You are an podcaster assistant your name is "Lisa". 
                 For now you have only to write a script for the intro of the podcast. 
                 The script should be 30 seconds long.
                 The script should explain the main topic of the podcast.
                 Explain how the episode lineup is going to be.
                 Remember the script will be read by a Text to Speech model.
                 
                 {lang_instruction}
                 Make sure ALL text is in the specified language.
                 """},
                {"role": "user", "content": f"Create an intro for a podcast about: {message}\nThis is the episode lineup: {episode_lineup}"},
            ]
        )
        
        text_to_speech(completion.choices[0].message.content, "first_episode")
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise

def create_episode(message, episode_number, previous_episode_script, language):
    """Send a message to OpenAI and return the response."""
    try:
        lang_instruction = language_prompts.get(language, language_prompts['en'])
        
        completion = openai.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
                {"role": "system", "content": f"""
                 You are an podcaster assistant your name is "Lisa". 
                 Write the script for episode {episode_number} of the podcast. 
                 The script should be 3 minutes long.
                 Previous episode script: {previous_episode_script}
                 
                 Remember this will be read by a Text to Speech model.
                 The output should be MAX 4000 characters.
                 
                 {lang_instruction}
                 Make sure ALL text is in the specified language.
                 """},
                {"role": "user", "content": f"Create episode {episode_number} about: {message}"},
            ]
        )
        text_to_speech(completion.choices[0].message.content, f"episode_{episode_number}")
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise



def start_chain(message, language):
    print("Starting chain")
    """Start the chain of the podcast."""
    episode_lineup = create_episode_lineup(message, language)
    print("Episode lineup created")
    first_episode = create_first_episode(message, episode_lineup, language)
    print("First episode created")
    episode_1 = create_episode(message, 1, first_episode, language)
    print("Episode 1 created")
    return episode_1
