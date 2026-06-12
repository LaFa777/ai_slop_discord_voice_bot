import asyncio
import logging
import os
import tempfile
import wave

import numpy as np
import torch

from .base import TTSProvider

logger = logging.getLogger(__name__)


class OmniVoiceProvider(TTSProvider):
    def __init__(self, ref_audio: str, ref_text: str | None = None) -> None:
        self.ref_audio = ref_audio
        self.ref_text = ref_text
        self._model = None

    async def synthesize(self, text: str) -> str:
        if self._model is None:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._load_model)
        loop = asyncio.get_event_loop()
        audio = await loop.run_in_executor(None, self._generate, text)
        return self._save_wav(audio)

    def _load_model(self) -> None:
        from omnivoice import OmniVoice

        if torch.cuda.is_available():
            torch.backends.cudnn.enabled = False
            logger.info("cuDNN disabled to avoid CTranslate2 conflict")

        logger.info("Loading OmniVoice model k2-fsa/OmniVoice...")
        self._model = OmniVoice.from_pretrained(
            "k2-fsa/OmniVoice",
            device_map="cuda:0" if torch.cuda.is_available() else "cpu",
            dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )
        logger.info("OmniVoice model loaded")

    def _generate(self, text: str) -> np.ndarray:
        try:
            return self._model.generate(
                text=text,
                ref_audio=self.ref_audio,
                ref_text=self.ref_text,
            )[0]
        except OSError:
            logger.warning("Whisper ASR cuDNN conflict, retrying with empty ref_text")
            return self._model.generate(
                text=text,
                ref_audio=self.ref_audio,
                ref_text="",
            )[0]

    def _save_wav(self, audio: np.ndarray) -> str:
        fd, tmp_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        with wave.open(tmp_path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes((audio * 32767).clip(-32768, 32767).astype("int16").tobytes())
        logger.info("OmniVoice TTS saved: %s (%d bytes)", tmp_path, os.path.getsize(tmp_path))
        return tmp_path
