import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Ты голосовой ассистент в Discord. Твоё имя — Discorder. "
    "Ты находишься в голосовом канале. "
    "Отвечай кратко, естественно, разговорным русским языком. "
    "Одно-два предложения, если не просят подробностей. "
    "Не используй маркдаун, эмодзи или форматирование — только чистый текст для озвучки."
)


class LLMResponder:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com", model: str = "deepseek_v4_flash") -> None:
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def respond(self, user_text: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                ],
                temperature=0.7,
                max_tokens=500,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("LLM error: %s", e)
            return "Извини, не могу ответить сейчас."
