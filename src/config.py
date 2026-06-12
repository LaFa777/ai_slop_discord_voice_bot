import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self) -> None:
        self.discord_token = os.getenv("DISCORD_TOKEN", "")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.bot_name = os.getenv("BOT_NAME", "discorder")
        wake_words_str = os.getenv("WAKE_WORDS", "discorder,дискордер,бот")
        self.wake_words = [w.strip().lower() for w in wake_words_str.split(",") if w.strip()]
        self.model_size = os.getenv("WHISPER_MODEL", "large-v3")
        self.device = os.getenv("WHISPER_DEVICE", "cuda")
        self.compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "float16")
        self.tts_provider = os.getenv("TTS_PROVIDER", "edge")
        self.tts_voice = os.getenv("TTS_VOICE", "ru-RU-DariyaNeural")
        self.tts_silero_speaker = os.getenv("TTS_SILERO_SPEAKER", "eugene")
        self.omnivoice_ref_audio = os.getenv("OMNIVOICE_REF_AUDIO", "sample.wav")
        self.omnivoice_ref_text = os.getenv("OMNIVOICE_REF_TEXT", "") or None
        self.llm_provider = os.getenv("LLM_PROVIDER", "deepseek")
        self.llm_model = os.getenv("LLM_MODEL", "deepseek_v4_flash")
        self.deepseek_host = os.getenv("DEEPSEEK_HOST", "https://api.deepseek.com")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.llm_history_size = int(os.getenv("LLM_HISTORY_SIZE", "10"))
        self.llm_conversation_ttl = int(os.getenv("LLM_CONVERSATION_TTL", "600"))


config = Config()
