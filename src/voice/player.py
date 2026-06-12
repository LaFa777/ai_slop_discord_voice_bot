import asyncio
import logging
import os

import discord

logger = logging.getLogger(__name__)


class VoicePlayer:
    def __init__(self) -> None:
        self._playing = False

    @property
    def is_playing(self) -> bool:
        return self._playing

    async def play(self, voice_client: discord.VoiceClient, audio_path: str) -> None:
        if not voice_client or not voice_client.is_connected():
            _cleanup(audio_path)
            return

        self._playing = True

        def _after(error: Exception | None) -> None:
            if error:
                logger.error("TTS playback error: %s", error)
            _cleanup(audio_path)

        try:
            source = discord.FFmpegPCMAudio(audio_path)

            if voice_client.is_playing():
                voice_client.stop_playing()

            voice_client.play(source, after=_after)

            while voice_client.is_playing():
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error("Failed to start TTS playback: %s", e)
            _cleanup(audio_path)
        finally:
            self._playing = False


def _cleanup(path: str) -> None:
    try:
        if os.path.exists(path):
            os.unlink(path)
    except OSError:
        pass
