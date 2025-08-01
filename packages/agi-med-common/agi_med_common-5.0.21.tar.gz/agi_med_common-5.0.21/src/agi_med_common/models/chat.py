from datetime import datetime
from typing import Any, List, Dict, Literal

from agi_med_common.models.chat_item import ChatItem, ReplicaItem, OuterContextItem
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
        return first_nonnull(map(_get_resource_id, obj))
    if isinstance(obj, dict) and obj.get("type") == "resource_id":
        return _get_str_field(obj, "resource_id")
    return None


def _get_command(obj: Content) -> dict | None:
    if isinstance(obj, list):
        return first_nonnull(map(_get_command, obj))
    if isinstance(obj, dict) and obj.get("type") == "command":
        return _get_str_field(obj, "command")
    return None


def _get_widget(obj: Content) -> Widget | None:
    if isinstance(obj, list):
        return first_nonnull(map(_get_widget, obj))
    if isinstance(obj, Widget):
        return obj
    return None


# todo fix: generalize functions above


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

    @property
    def command(self) -> dict | None:
        return _get_command(self.content)

    @property
    def widget(self) -> Widget | None:
        return _get_widget(self.content)

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

    @classmethod
    def parse(self, chat_obj: str | dict) -> "Chat":
        return _parse_chat_compat(chat_obj)


def convert_replica_item_to_message(replica: ReplicaItem) -> ChatMessage:
    resource_id = (replica.resource_id or None) and {"type": "resource_id", "resource_id": replica.resource_id}
    body = replica.body
    command = replica.command
    widget = replica.widget

    content = list(filter(None, [body, resource_id, command, widget]))
    if len(content) == 0:
        content = ""
    elif len(content) == 1:
        content = content[0]

    kwargs = dict(
        content=content,
        date_time=replica.date_time,
        extra=replica.extra,
    )
    if not replica.role:
        return HumanMessage(**kwargs)
    return AIMessage(
        **kwargs,
        state=replica.state,
        extra=dict(
            action=replica.action,
            moderation=replica.moderation,
        ),
    )


def convert_outer_context_to_context(octx: OuterContextItem) -> Context:
    # legacy: eliminate
    context = Context(
        client_id=octx.client_id,
        user_id=octx.user_id,
        session_id=octx.session_id,
        track_id=octx.track_id,
        extra=dict(
            sex=octx.sex,
            age=octx.age,
            parent_session_id=octx.parent_session_id,
            entrypoint_key=octx.entrypoint_key,
            language_code=octx.language_code,
        ),
    )
    return context


def convert_chat_item_to_chat(chat_item: ChatItem) -> Chat:
    # legacy: eliminate
    context = convert_outer_context_to_context(chat_item.outer_context)
    messages = [convert_replica_item_to_message(replica) for replica in chat_item.inner_context.replicas]
    res = Chat(context=context, messages=messages)
    return res


def convert_context_to_outer_context(context: Context) -> OuterContextItem:
    # legacy: eliminate
    extra = context.extra or {}
    return OuterContextItem(
        client_id=context.client_id,
        user_id=context.user_id,
        session_id=context.session_id,
        track_id=context.track_id,
        sex=extra.get("sex"),
        age=extra.get("age"),
        parent_session_id=extra.get("parent_session_id"),
        entrypoint_key=extra.get("entrypoint_key"),
        language_code=extra.get("language_code"),
    )


def convert_message_to_replica_item(message: ChatMessage) -> ReplicaItem | None:
    # legacy: eliminate
    m_type = message.type
    if m_type in {"ai", "human"}:
        role = m_type == "ai"
    else:
        return None

    extra = message.extra or {}
    action = extra.pop("action")
    moderation = extra.pop("moderation")

    kwargs = dict(
        role=role,
        body=message.body,
        resource_id=message.resource_id,
        command=message.command,
        widget=message.widget,
        date_time=message.date_time,
        extra=extra or None,
        state=getattr(message, "state", ""),
        action=action,
        moderation=moderation,
    )
    return ReplicaItem(**kwargs)


def convert_chat_to_chat_item(chat: Chat) -> ChatItem:
    # legacy: eliminate
    return ChatItem(
        outer_context=convert_context_to_outer_context(chat.context),
        inner_context=dict(replicas=list(map(convert_message_to_replica_item, chat.messages))),
    )


def parse_chat_item_as_chat(chat_obj: str | dict) -> Chat:
    # legacy: eliminate
    chat_item = ChatItem.parse(chat_obj)
    res = convert_chat_item_to_chat(chat_item)
    return res


def _parse_chat(chat_obj: str | dict) -> Chat:
    if isinstance(chat_obj, dict):
        return Chat.model_validate(chat_obj)

    return Chat.model_validate_json(chat_obj)


def _parse_chat_compat(chat_obj: str | dict) -> Chat:
    # legacy: eliminate
    try:
        return _parse_chat(chat_obj)
    except Exception:
        return parse_chat_item_as_chat(chat_obj)
