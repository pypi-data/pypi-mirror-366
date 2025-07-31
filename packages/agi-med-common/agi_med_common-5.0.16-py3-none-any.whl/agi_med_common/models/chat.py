from datetime import datetime
from typing import Any, List, Dict, Literal

from agi_med_common.models.widget import Widget
from agi_med_common.type_union import TypeUnion
from agi_med_common.utils import first_nonnull
from pydantic import Field

from ._base import _Base


_DT_FORMAT: str = "%Y-%m-%d-%H-%M-%S"
_EXAMPLE_DT: str = datetime(year=1970, month=1, day=1).strftime(_DT_FORMAT)
StrDict = Dict[str, Any]
ContentBase = str | Widget | StrDict
Content = ContentBase | List[ContentBase]


def now_pretty() -> str:
    return datetime.now().strftime(_DT_FORMAT)


class Context(_Base):
    client_id: str = Field("", examples=["543216789"])
    user_id: str = Field("", examples=["123456789"])
    session_id: str = Field("", examples=["987654321"])
    track_id: str = Field(examples=["Hello"])
    extra: StrDict | None = Field(None, examples=[None])

    def create_id(self, short: bool = False) -> str:
        uid, sid, cid = self.user_id, self.session_id, self.client_id
        if short:
            return f"{cid}_{uid}_{sid}"
        return f"client_{cid}_user_{uid}_session_{sid}"


def _get_str_field(obj: dict, field) -> str | None:
    if not isinstance(obj, dict):
        return None
    text = obj.get(field)
    if text is not None and isinstance(text, str):
        return text
    return None


def _get_text(obj: Content) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return "".join(map(_get_text, obj))
    if isinstance(obj, dict) and obj.get("type") == "text":
        return _get_str_field(obj, "text") or ""
    return ""


def _get_resource_id(obj: Content) -> str | None:
    if isinstance(obj, list):
        return first_nonnull(_get_str_field(el, "resource_id") for el in obj)
    if isinstance(obj, dict) and obj.get("type") == "resource_id":
        return _get_str_field(obj, "resource_id")
    return None


class BaseMessage(_Base):
    type: str
    content: Content = Field("", examples=["Привет"])
    date_time: str = Field(default_factory=now_pretty, examples=[_EXAMPLE_DT])
    extra: StrDict | None = Field(None, examples=[None])

    @property
    def text(self) -> str:
        return _get_text(self.content)

    @property
    def resource_id(self) -> str | None:
        return _get_resource_id(self.content)

    @staticmethod
    def DATETIME_FORMAT() -> str:
        return _DT_FORMAT

    def with_now_datetime(self):
        return self.model_copy(update=dict(date_time=now_pretty()))


class HumanMessage(BaseMessage):
    type: Literal["human"] = "human"


class AIMessage(BaseMessage):
    type: Literal["ai"] = "ai"
    state: str = Field("", examples=["COLLECTION"])


class MiscMessage(BaseMessage):
    type: Literal["misc"] = "misc"


ChatMessage = TypeUnion[HumanMessage, AIMessage, MiscMessage]


class Chat(_Base):
    context: Context
    messages: List[ChatMessage] = []

    def create_id(self, short: bool = False) -> str:
        return self.context.create_id(short)
