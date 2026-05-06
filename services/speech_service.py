import io


def transcribe_audio(client, audio_bytes):

    if not audio_bytes:
        return ""

    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "speech.wav"

    transcript = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=audio_file
    )

    return transcript.text
