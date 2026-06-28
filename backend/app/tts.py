import uuid
from pathlib import Path

import edge_tts


AUDIO_DIR = Path("data/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


VOICE_MAP = {
    "english": "en-US-JennyNeural",
    "hindi": "hi-IN-SwaraNeural",
    "hinglish": "hi-IN-SwaraNeural",
    "punjabi": "pa-IN-VaaniNeural",
    "roman_punjabi": "pa-IN-VaaniNeural",
    "french": "fr-FR-DeniseNeural",
    "spanish": "es-ES-ElviraNeural",
    "auto": "en-US-JennyNeural",
}


async def text_to_speech(text: str, language: str = "auto") -> str:
    voice = VOICE_MAP.get(language, VOICE_MAP["auto"])
    file_path = AUDIO_DIR / f"{uuid.uuid4()}.mp3"

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(file_path))

    return str(file_path)