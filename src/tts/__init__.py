from .base import TTSProvider
from .edge import EdgeTTSProvider
from .silero import SileroProvider


def create_tts(provider: str, voice: str = "",
               silero_speaker: str = "") -> TTSProvider:
    if provider == "silero":
        return SileroProvider(speaker=silero_speaker or "eugene")
    return EdgeTTSProvider(voice=voice or "ru-RU-DariyaNeural")
