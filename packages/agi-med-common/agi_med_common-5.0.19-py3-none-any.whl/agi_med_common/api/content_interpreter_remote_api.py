from pydantic import BaseModel
from agi_med_common import ChatItem


class ContentInterpreterRemoteResponse(BaseModel):
    interpretation: str
    resource_fname: str
    resource: bytes


class ContentInterpreterRemoteAPI:
    def interpret_remote(
        self,
        kind: str,
        query: str,
        resource: bytes,
        chat: ChatItem | None = None,
        request_id: str = "",
    ) -> ContentInterpreterRemoteResponse:
        raise NotImplementedError
