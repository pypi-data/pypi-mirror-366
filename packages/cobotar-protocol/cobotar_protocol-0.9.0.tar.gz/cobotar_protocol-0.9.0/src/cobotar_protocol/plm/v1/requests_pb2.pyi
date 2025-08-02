from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ProcessAtLocationMessage(_message.Message):
    __slots__ = ("request_id", "location_id")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    location_id: str
    def __init__(self, request_id: _Optional[str] = ..., location_id: _Optional[str] = ...) -> None: ...

class TasksForAgentMessage(_message.Message):
    __slots__ = ("request_id", "instance_id", "agent_id")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    instance_id: str
    agent_id: str
    def __init__(self, request_id: _Optional[str] = ..., instance_id: _Optional[str] = ..., agent_id: _Optional[str] = ...) -> None: ...
