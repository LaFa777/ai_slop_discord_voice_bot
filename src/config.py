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
        self.tts_voice = os.getenv("TTS_VOICE", "ru-RU-DariyaNeural")
        self.llm_provider = os.getenv("LLM_PROVIDER", "deepseek")
        self.llm_model = os.getenv("LLM_MODEL", "deepseek_v4_flash")
        self.deepseek_host = os.getenv("DEEPSEEK_HOST", "https://api.deepseek.com")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")


config = Config()
