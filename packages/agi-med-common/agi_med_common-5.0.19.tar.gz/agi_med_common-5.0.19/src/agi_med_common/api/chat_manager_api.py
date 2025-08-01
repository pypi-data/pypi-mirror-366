from typing import List

from agi_med_common.models import ChatItem, ReplicaItem, DomainInfo, TrackInfo


class ChatManagerAPI:
    def get_domains(self, language_code: str, client_id: str) -> List[DomainInfo]:
        raise NotImplementedError

    def get_tracks(self, language_code: str, client_id: str) -> List[TrackInfo]:
        raise NotImplementedError

    def get_response(self, chat: ChatItem, request_id: str = "") -> List[ReplicaItem]:
        raise NotImplementedError
