from .base import TTSProvider
from .edge import EdgeTTSProvider
from .silero import SileroProvider
from .omnivoice import OmniVoiceProvider


def create_tts(provider: str, voice: str = "",
               silero_speaker: str = "",
               omnivoice_ref_audio: str = "",
               omnivoice_ref_text: str | None = None) -> TTSProvider:
    if provider == "silero":
        return SileroProvider(speaker=silero_speaker or "eugene")
    if provider == "omnivoice":
        return OmniVoiceProvider(
            ref_audio=omnivoice_ref_audio,
            ref_text=omnivoice_ref_text or None,
        )
    return EdgeTTSProvider(voice=voice or "ru-RU-DariyaNeural")
