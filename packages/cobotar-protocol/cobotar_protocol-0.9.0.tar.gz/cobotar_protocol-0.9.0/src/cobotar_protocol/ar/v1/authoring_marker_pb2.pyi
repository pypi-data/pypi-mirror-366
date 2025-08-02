from common.v1 import agent_pb2 as _agent_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MarkerNewMessage(_message.Message):
    __slots__ = ("name", "description", "marker_text")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MARKER_TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    marker_text: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., marker_text: _Optional[str] = ...) -> None: ...

class MarkerUpdateMessage(_message.Message):
    __slots__ = ("id", "name", "description", "marker_text", "agents", "ar_disappear_distance")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MARKER_TEXT_FIELD_NUMBER: _ClassVar[int]
    AGENTS_FIELD_NUMBER: _ClassVar[int]
    AR_DISAPPEAR_DISTANCE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    marker_text: str
    agents: _containers.RepeatedCompositeFieldContainer[_agent_pb2.Agent]
    ar_disappear_distance: int
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., marker_text: _Optional[str] = ..., agents: _Optional[_Iterable[_Union[_agent_pb2.Agent, _Mapping]]] = ..., ar_disappear_distance: _Optional[int] = ...) -> None: ...

class MarkerDeleteMessage(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...
