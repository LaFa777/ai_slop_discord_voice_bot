from abc import ABC, abstractmethod
from pathlib import Path

_PROMPT_FILE = Path(__file__).parent / "system_prompt.txt"


class LLMProvider(ABC):
    @abstractmethod
    async def respond(self, user_text: str, history: list[dict] | None = None) -> str:
        ...

    def get_system_prompt(self) -> str:
        return _PROMPT_FILE.read_text("utf-8").strip()
