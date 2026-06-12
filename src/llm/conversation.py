import time
import logging

from .base import LLMProvider

logger = logging.getLogger(__name__)


class ConversationManager:
    def __init__(self, llm: LLMProvider, max_messages: int = 10,
                 ttl_seconds: int | None = 600) -> None:
        self.llm = llm
        self.max_messages = max_messages
        self.ttl_seconds = ttl_seconds
        self._history: dict[int, list[dict]] = {}
        self._last_activity: dict[int, float] = {}

    async def respond(self, channel_id: int, user_text: str) -> str:
        self._check_expiry(channel_id)
        history = self._history.get(channel_id, [])
        response = await self.llm.respond(user_text, history)
        self._append(channel_id, user_text, response)
        return response

    def clear(self, channel_id: int) -> None:
        self._history.pop(channel_id, None)
        self._last_activity.pop(channel_id, None)
        logger.info("Conversation cleared for channel %s", channel_id)

    def _append(self, channel_id: int, user_text: str, response: str) -> None:
        if channel_id not in self._history:
            self._history[channel_id] = []
        self._history[channel_id].append({"role": "user", "content": user_text})
        self._history[channel_id].append({"role": "assistant", "content": response})
        limit = self.max_messages * 2
        if len(self._history[channel_id]) > limit:
            self._history[channel_id] = self._history[channel_id][-limit:]
        self._last_activity[channel_id] = time.time()

    def _check_expiry(self, channel_id: int) -> None:
        if self.ttl_seconds is None:
            return
        last = self._last_activity.get(channel_id)
        if last is not None and time.time() - last > self.ttl_seconds:
            self.clear(channel_id)
