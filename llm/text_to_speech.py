from pathlib import Path
from llm.config import openai
import os
from pydub import AudioSegment

def add_intro_to_audio(intro_path, main_audio_path, output_path):
    """
    Add an intro audio to the beginning of the main audio and save to output path.
    """
    intro = AudioSegment.from_mp3(intro_path)
    main_audio = AudioSegment.from_mp3(main_audio_path)
    combined = intro + main_audio
    combined.export(output_path, format="mp3")

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
    
    # Define the path to the intro audio
    # Use a relative path from the project root to the assets directory
    intro_path = str(Path(__file__).parent.parent / "assets" / "intro.mp3")
    
    # Create a temporary path for the main audio
    temp_main_audio_path = f"{file_path}.temp.mp3"
    
    # Save the main audio to the temporary path
    response.stream_to_file(temp_main_audio_path)
    
    # Combine the intro and main audio
    add_intro_to_audio(intro_path, temp_main_audio_path, file_path)
    
    # Remove the temporary main audio file
    os.remove(temp_main_audio_path)
    return file_path
