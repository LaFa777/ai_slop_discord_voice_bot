from .base import LLMProvider
from .conversation import ConversationManager
from .deepseek import DeepSeekResponder
from .ollama import OllamaResponder


def create_llm(provider: str, api_key: str = "", model: str = "",
               deepseek_host: str = "", ollama_host: str = "") -> LLMProvider:
    if provider == "ollama":
        return OllamaResponder(host=ollama_host, model=model)
    return DeepSeekResponder(api_key=api_key, base_url=deepseek_host, model=model)
