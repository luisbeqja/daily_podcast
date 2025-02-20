from llm.config import logger, openai
from llm.text_to_speech import text_to_speech

def get_response(message):
    """Send a message to OpenAI and return the response."""
    try:
        completion = openai.chat.completions.create(
        model="gpt-4o-mini",  # Updated model name
        messages=[
                {"role": "system", "content": """
                 You are an podcaster assistant your name is "Lisa". 
                 For now you have only to write a script for the first episode of the podcast. 
                 The script should be in 30 seconds long.
                 The script should explain the main topic of the podcast.
                 
                 Remember the script, is then going to be read by a Text to Speech model by OpenAI with voice alloy.
                 """},
                {"role": "user", "content": message},
            ]
        )
        text_to_speech(completion.choices[0].message.content, "first_episode")
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise
