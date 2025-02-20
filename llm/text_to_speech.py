from pathlib import Path
from llm.config import openai


def text_to_speech(text, file_name):
    speech_file_path = Path(__file__).parent / "episodes" / f"{file_name}.mp3"
    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova",  # Alloy has a more professional, podcast-like voice
        input=text,
        speed=1.12,  # Slightly slower for better clarity
        response_format="mp3",  # Ensure high quality audio
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path
