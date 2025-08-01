from typing import Tuple

from agi_med_common.file_storage import ResourceId
from agi_med_common.models import ChatItem


Interpretation = str


class ContentInterpreterAPI:
    def interpret(
        self,
        kind: str,
        query: str,
        resource_id: str = "",
        chat: ChatItem | None = None,
        request_id: str = "",
    ) -> Tuple[Interpretation, ResourceId | None]:
        raise NotImplementedError
