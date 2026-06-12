import asyncio
import logging
import os
import tempfile
import wave

import numpy as np

from .base import TTSProvider

logger = logging.getLogger(__name__)

SILERO_MODEL_URL = "https://models.silero.ai/models/tts/ru/v5_ru.pt"


class SileroProvider(TTSProvider):
    def __init__(self, speaker: str = "eugene") -> None:
        self.speaker = speaker
        self._model = None
        self._loaded = False

    async def synthesize(self, text: str) -> str:
        fd, tmp_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._generate_sync, text, tmp_path)
        logger.info("Silero TTS saved: %s (%d bytes)", tmp_path, os.path.getsize(tmp_path))
        return tmp_path

    def _generate_sync(self, text: str, output_path: str) -> None:
        if not self._loaded:
            self._load_model()

        audio = self._model.apply_tts(
            text=text,
            speaker=self.speaker,
            sample_rate=48000,
            put_accent=True,
            put_yo=True,
        )

        samples = (audio.numpy().flatten() * 32767).clip(-32768, 32767).astype("int16")

        with wave.open(output_path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(48000)
            wf.writeframes(samples.tobytes())

    def _load_model(self) -> None:
        import torch

        device = torch.device("cpu")
        torch.set_num_threads(4)

        model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".silero")
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "v5_ru.pt")

        if not os.path.isfile(model_path):
            logger.info("Downloading Silero model v5_ru (~200MB)...")
            torch.hub.download_url_to_file(SILERO_MODEL_URL, model_path)

        model = torch.package.PackageImporter(model_path).load_pickle("tts_models", "model")
        model.to(device)
        self._model = model
        self._loaded = True
        logger.info("Silero TTS loaded on %s (speakers: %s)", device, model.speakers)
