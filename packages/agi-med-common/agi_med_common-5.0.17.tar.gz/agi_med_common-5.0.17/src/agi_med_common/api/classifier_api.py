from typing import List

from agi_med_common.models import ChatItem


Value = str


class ClassifierAPI:
    def get_values(self) -> List[Value]:
        raise NotImplementedError

    def evaluate(self, chat: ChatItem, request_id: str = "") -> Value:
        raise NotImplementedError
