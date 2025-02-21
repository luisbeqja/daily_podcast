from pathlib import Path
from llm.config import openai
import os


def text_to_speech(text, file_path):
    """
    Convert text to speech and save to a specific path.
    file_path should be the full path including user directory
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Add .mp3 extension if not present
    if not file_path.endswith('.mp3'):
        file_path = f"{file_path}.mp3"

    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova",  # Alloy has a more professional, podcast-like voice
        input=text,
        speed=1.12,  # Slightly slower for better clarity
        response_format="mp3",  # Ensure high quality audio
    )
    
    # Stream the response to the specified file path
    response.stream_to_file(file_path)
    return file_path
