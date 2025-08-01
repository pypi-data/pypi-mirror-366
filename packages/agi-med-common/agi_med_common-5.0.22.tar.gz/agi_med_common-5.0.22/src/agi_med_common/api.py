from typing import List, Tuple

from agi_med_common.models import ChatItem, ReplicaItem, DomainInfo, TrackInfo
from pydantic import BaseModel


Value = str
Interpretation = str
ResourceId = str


class ChatManagerAPI:
    def get_domains(self, language_code: str, client_id: str) -> List[DomainInfo]:
        raise NotImplementedError

    def get_tracks(self, language_code: str, client_id: str) -> List[TrackInfo]:
        raise NotImplementedError

    def get_response(self, chat: ChatItem, request_id: str = "") -> List[ReplicaItem]:
        raise NotImplementedError


class TextGeneratorAPI:
    def process(self, chat: ChatItem, request_id: str = "") -> str:
        raise NotImplementedError


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


class ClassifierAPI:
    def get_values(self) -> List[Value]:
        raise NotImplementedError

    def evaluate(self, chat: ChatItem, request_id: str = "") -> Value:
        raise NotImplementedError


class CriticAPI:
    def evaluate(self, text: str, chat: ChatItem | None = None, request_id: str = "") -> float:
        raise NotImplementedError


class ContentInterpreterAPI:
    def interpret(
        self, kind: str, query: str, resource_id: str = "", chat: ChatItem | None = None, request_id: str = ""
    ) -> Tuple[Interpretation, ResourceId | None]:
        raise NotImplementedError


class TextProcessorAPI:
    def process(self, text: str, chat: ChatItem | None = None, request_id: str = "") -> str:
        raise NotImplementedError
