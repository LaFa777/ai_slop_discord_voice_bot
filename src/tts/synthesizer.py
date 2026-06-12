import asyncio
import logging
import os
import tempfile
import wave

import edge_tts
import numpy as np

logger = logging.getLogger(__name__)

SILERO_MODEL_URL = "https://models.silero.ai/models/tts/ru/v5_ru.pt"


class TTSSynthesizer:
    def __init__(self, voice: str = "ru-RU-DariyaNeural") -> None:
        self.edge_voice = voice
        self.silero_voice = "eugene"
        self._silero_model = None
        self._silero_loaded = False

    async def synthesize(self, text: str) -> str:
        try:
            return await self._edge_generate(text)
        except Exception:
            logger.warning("Edge TTS failed, falling back to Silero", exc_info=True)
            return await self._silero_generate(text)

    async def _edge_generate(self, text: str) -> str:
        fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        communicate = edge_tts.Communicate(text.strip(), self.edge_voice)
        await communicate.save(tmp_path)
        logger.info("Edge TTS saved: %s (%d bytes)", tmp_path, os.path.getsize(tmp_path))
        return tmp_path

    async def _silero_generate(self, text: str) -> str:
        fd, tmp_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._silero_sync, text, tmp_path)
        logger.info("Silero TTS saved: %s (%d bytes)", tmp_path, os.path.getsize(tmp_path))
        return tmp_path

    def _silero_sync(self, text: str, output_path: str) -> None:
        if not self._silero_loaded:
            self._load_silero()

        audio = self._silero_model.apply_tts(
            text=text,
            speaker=self.silero_voice,
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

    def _load_silero(self) -> None:
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
        self._silero_model = model
        self._silero_loaded = True
        logger.info("Silero TTS loaded on %s (voices: %s)", device, model.speakers)
