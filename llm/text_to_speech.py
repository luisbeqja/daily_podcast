from pathlib import Path
from llm.config import openai


def text_to_speech(text, file_name):
    speech_file_path = Path(__file__).parent / "episodes" / f"{file_name}.mp3"
    response = openai.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path
