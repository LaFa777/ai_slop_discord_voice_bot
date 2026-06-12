import logging
import os
import tempfile

import edge_tts

from .base import TTSProvider

logger = logging.getLogger(__name__)


class EdgeTTSProvider(TTSProvider):
    def __init__(self, voice: str = "ru-RU-DariyaNeural") -> None:
        self.voice = voice

    async def synthesize(self, text: str) -> str:
        fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        communicate = edge_tts.Communicate(text.strip(), self.voice)
        await communicate.save(tmp_path)
        logger.info("Edge TTS saved: %s (%d bytes)", tmp_path, os.path.getsize(tmp_path))
        return tmp_path
