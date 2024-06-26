from elevenlabs import play
from elevenlabs.client import ElevenLabs
from config import ELEVEN_API_KEY

def text2Speech(text: str, output_file: str = "audio_file.mp3"):
    client = ElevenLabs(api_key=ELEVEN_API_KEY)

    audio = client.generate(
        text=text,
        voice="Rachel",
        model="eleven_multilingual_v2"
    )
    # Save the audio to a file
    with open(output_file, 'wb') as f:
        for chunk in audio:
            f.write(chunk)

