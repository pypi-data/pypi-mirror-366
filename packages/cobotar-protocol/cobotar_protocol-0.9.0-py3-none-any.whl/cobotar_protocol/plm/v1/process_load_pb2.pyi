from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ProcessLoadMessage(_message.Message):
    __slots__ = ("request_id", "process_id", "location_id", "abort_running_process")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    PROCESS_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    ABORT_RUNNING_PROCESS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    process_id: str
    location_id: str
    abort_running_process: bool
    def __init__(self, request_id: _Optional[str] = ..., process_id: _Optional[str] = ..., location_id: _Optional[str] = ..., abort_running_process: bool = ...) -> None: ...
