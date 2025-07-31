from agi_med_common.models import ChatItem


class TextGeneratorAPI:
    def process(self, chat: ChatItem, request_id: str = "") -> str:
        raise NotImplementedError
