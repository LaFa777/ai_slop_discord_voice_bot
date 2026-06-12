import logging
from ollama import AsyncClient

from .base import LLMProvider

logger = logging.getLogger(__name__)


class OllamaResponder(LLMProvider):
    def __init__(self, host: str, model: str) -> None:
        self.client = AsyncClient(host=host)
        self.model = model

    def get_system_prompt(self) -> str:
        return "/no_think " + super().get_system_prompt()

    async def respond(self, user_text: str) -> str:
        try:
            response = await self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": user_text},
                ],
                think=False,
                options={"temperature": 0.7, "num_predict": 500},
            )
            return response.message.content or ""
        except Exception as e:
            logger.error("LLM error: %s", e)
            return "Извини, не могу ответить сейчас."
