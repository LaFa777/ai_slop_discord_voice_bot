import logging

import numpy as np
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class Transcriber:
    def __init__(self, model_size: str = "large-v3", device: str = "cuda", compute_type: str = "float16") -> None:
        logger.info("Loading whisper model '%s' on %s (%s)…", model_size, device, compute_type)
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        logger.info("Whisper model loaded")

    @staticmethod
    def convert_audio(pcm48_stereo: bytes) -> np.ndarray:
        audio = np.frombuffer(pcm48_stereo, dtype=np.int16)
        audio = audio.reshape(-1, 2).mean(axis=1).astype(np.float32)
        audio = audio / 32768.0
        return audio

    def transcribe(self, audio: np.ndarray) -> str:
        audio_16k = audio[::3]
        segments, _ = self.model.transcribe(
            audio_16k,
            beam_size=5,
            language="ru",
            vad_filter=True,
        )
        text = " ".join(s.text.strip() for s in segments)
        return text
