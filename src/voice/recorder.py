import asyncio
import logging
import threading
from typing import Callable, Awaitable

import discord
from discord.ext import voice_recv

logger = logging.getLogger(__name__)


class SpeechRecognitionSink(voice_recv.AudioSink):
    def __init__(
        self,
        on_utterance: Callable[[discord.Member, bytes], Awaitable[None]],
    ) -> None:
        super().__init__()
        self._on_utterance = on_utterance
        self._buffers: dict[int, bytearray] = {}
        self._lock = threading.Lock()
        self.paused = False

    def wants_opus(self) -> bool:
        return False

    @voice_recv.AudioSink.listener()
    def on_voice_member_speaking_start(self, member: discord.Member) -> None:
        with self._lock:
            self._buffers[member.id] = bytearray()
        logger.debug("+++ speaking start: %s", member.display_name)

    @voice_recv.AudioSink.listener()
    def on_voice_member_speaking_stop(self, member: discord.Member) -> None:
        with self._lock:
            audio = bytes(self._buffers.pop(member.id, bytearray()))
        logger.debug("--- speaking stop : %s  (%d bytes)", member.display_name, len(audio))
        if audio and not self.paused:
            loop = self.client and self.client.loop
            if loop and not loop.is_closed():
                asyncio.run_coroutine_threadsafe(
                    self._on_utterance(member, audio),
                    loop,
                )

    def write(self, user: discord.User | discord.Member | None, data: voice_recv.VoiceData) -> None:
        if self.paused or user is None:
            return
        with self._lock:
            buf = self._buffers.get(user.id)
            if buf is not None:
                buf.extend(data.pcm)

    def cleanup(self) -> None:
        with self._lock:
            self._buffers.clear()
