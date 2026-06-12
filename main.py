#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "discord.py[voice] @ git+https://github.com/Rapptz/discord.py.git@master",
#   "discord-ext-voice-recv @ git+https://github.com/rdphillips7/discord-ext-voice-recv.git@main",
#   "davey>=0.1.0",
#   "faster-whisper>=1.0.0",
#   "edge-tts>=6.0.0",
#   "ollama>=0.4.0",
#   "openai>=1.0.0",
#   "python-dotenv>=1.0.0",
#   "numpy>=1.24.0",
#   "scipy>=1.10.0",
#   "torch>=2.0.0",
# ]
# ///

import asyncio
import logging

import discord
from discord.ext import voice_recv

from src.config import config
from src.llm import create_llm, ConversationManager
from src.stt.transcriber import Transcriber
from src.tts import create_tts, TTSProvider
from src.voice.player import VoicePlayer
from src.voice.recorder import SpeechRecognitionSink

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("discorder")


class DiscorderBot(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

        self.tree = discord.app_commands.CommandTree(self)
        self.transcriber: Transcriber | None = None
        self.conversations: ConversationManager | None = None
        self.tts: TTSProvider | None = None
        self.player: VoicePlayer | None = None
        self.recorder: SpeechRecognitionSink | None = None
        self.voice_client: voice_recv.VoiceRecvClient | None = None
        self._processing = False

    async def setup_hook(self) -> None:
        logger.info("Loading whisper model…")
        self.transcriber = Transcriber(
            model_size=config.model_size,
            device=config.device,
            compute_type=config.compute_type,
        )
        llm = create_llm(
            provider=config.llm_provider,
            api_key=config.deepseek_api_key,
            model=config.llm_model,
            deepseek_host=config.deepseek_host,
            ollama_host=config.ollama_host,
        )
        self.conversations = ConversationManager(
            llm=llm,
            max_messages=config.llm_history_size,
            ttl_seconds=config.llm_conversation_ttl,
        )
        self.tts = create_tts(
            provider=config.tts_provider,
            voice=config.tts_voice,
            silero_speaker=config.tts_silero_speaker,
        )
        self.player = VoicePlayer()

        @self.tree.command(name="join", description="Подключиться к голосовому каналу")
        async def join(interaction: discord.Interaction, channel: discord.VoiceChannel | None = None) -> None:
            if channel is None:
                if interaction.user and interaction.user.voice and interaction.user.voice.channel:
                    channel = interaction.user.voice.channel
                else:
                    await interaction.response.send_message("Ты не в голосовом канале.", ephemeral=True)
                    return

            if self.voice_client and self.voice_client.is_connected():
                await self.voice_client.disconnect()

            self.voice_client = await channel.connect(cls=voice_recv.VoiceRecvClient)
            self._start_listening()
            await interaction.response.send_message(
                f"Подключился к каналу **{channel.name}**. Слушаю…",
                ephemeral=True,
            )

        @self.tree.command(name="leave", description="Отключиться от голосового канала")
        async def leave(interaction: discord.Interaction) -> None:
            if self.voice_client and self.voice_client.is_connected():
                if self.voice_client.is_playing():
                    self.voice_client.stop_playing()
                self.voice_client.stop_listening()
                channel_id = self.voice_client.channel.id
                await self.voice_client.disconnect()
                self.voice_client = None
                self.recorder = None
                if self.conversations:
                    self.conversations.clear(channel_id)
                await interaction.response.send_message("Отключился.", ephemeral=True)
            else:
                await interaction.response.send_message("Я не в голосовом канале.", ephemeral=True)

        await self.tree.sync()
        logger.info("Commands synced, bot ready")

    def _start_listening(self) -> None:
        if not self.voice_client or not self.voice_client.is_connected():
            return

        self.recorder = SpeechRecognitionSink(
            on_utterance=self._handle_utterance,
        )
        self.voice_client.listen(self.recorder)

        ds = self.voice_client._connection.dave_session
        if ds is not None and hasattr(ds, "set_passthrough_mode"):
            ds.set_passthrough_mode(True, 10)
            logger.info("DAVE passthrough ON  ready=%s  proto=%s  can_encrypt=%s",
                ds.ready,
                ds.protocol_version,
                self.voice_client._connection.can_encrypt,
            )

        logger.info("Listening started")

    async def _handle_utterance(self, member: discord.Member, audio_bytes: bytes) -> None:
        if self._processing:
            return
        self._processing = True

        try:
            if self.recorder:
                self.recorder.paused = True

            audio_array = self.transcriber.convert_audio(audio_bytes)
            text = self.transcriber.transcribe(audio_array)
            logger.info("[%s] → %s", member.display_name, text)

            if not text.strip():
                logger.info("Empty transcription — skip")
                return

            text_lower = text.lower()
            hit = next((w for w in config.wake_words if w in text_lower), None)
            if hit is None:
                logger.info("No wake word in transcription — skip")
                return

            logger.info("Wake word '%s' matched, calling LLM…", hit)
            channel_id = self.voice_client.channel.id
            response = await self.conversations.respond(channel_id, text)
            logger.info("LLM response: %s", response)

            if not response.strip():
                return

            logger.info("Generating TTS…")
            tts_path = await self.tts.synthesize(response)
            logger.info("TTS ready (%s), playing…", tts_path)
            await self.player.play(self.voice_client, tts_path)
            logger.info("Playback finished")
        except Exception:
            logger.exception("Error in _handle_utterance")
        finally:
            self._processing = False
            if self.recorder:
                self.recorder.paused = False

    async def on_ready(self) -> None:
        logger.info("Logged in as %s (%s)", self.user, self.user.id)


async def main() -> None:
    if not config.discord_token:
        logger.error("DISCORD_TOKEN not set in .env")
        return
    if config.llm_provider == "deepseek" and not config.deepseek_api_key:
        logger.error("DEEPSEEK_API_KEY not set in .env")
        return

    bot = DiscorderBot()
    await bot.start(config.discord_token)


if __name__ == "__main__":
    asyncio.run(main())
