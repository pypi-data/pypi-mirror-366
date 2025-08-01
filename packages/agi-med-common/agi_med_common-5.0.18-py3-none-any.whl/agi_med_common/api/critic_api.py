from agi_med_common.models import ChatItem


class CriticAPI:
    def evaluate(self, text: str, chat: ChatItem | None = None, request_id: str = "") -> float:
        raise NotImplementedError
