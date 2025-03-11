import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
        
def ElevenLabsTextToSpeech(text, file_path):
    """
    Convert text to speech using ElevenLabs and save to a specific path.
    file_path should be the full path including user directory
    """
    try:
        load_dotenv()
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        print('path', os.path.dirname(file_path))
        
        client = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
        )

        # Get the audio as a generator
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id="5l5f8iK3YPeGga21rQIX",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        
        # Convert generator to bytes
        audio_bytes = b''.join(chunk for chunk in audio_generator)
        
        # Add .mp3 extension if not present
        if not file_path.endswith('.mp3'):
            file_path = f"{file_path}.mp3"
        
        # Write the audio data to file
        with open(file_path, 'wb') as audio_file:
            audio_file.write(audio_bytes)
        
        return file_path
        
    except Exception as e:
        print(f"An error occurred: {e}")
        raise