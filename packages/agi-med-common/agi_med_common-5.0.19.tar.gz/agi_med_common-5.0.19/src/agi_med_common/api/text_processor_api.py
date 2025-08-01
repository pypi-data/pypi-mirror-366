from agi_med_common import ChatItem


class TextProcessorAPI:
    def process(self, text: str, chat: ChatItem | None = None, request_id: str = "") -> str:
        raise NotImplementedError
