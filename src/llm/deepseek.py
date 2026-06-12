import logging
from openai import AsyncOpenAI

from .base import LLMProvider

logger = logging.getLogger(__name__)


class DeepSeekResponder(LLMProvider):
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def respond(self, user_text: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": user_text},
                ],
                temperature=0.7,
                max_tokens=500,
                extra_body={"thinking": {"type": "disabled"}},
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("LLM error: %s", e)
            return "Извини, не могу ответить сейчас."
