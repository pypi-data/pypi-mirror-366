import types
from threading import Event
from typing import Any, ClassVar, Literal

from _typeshed import Incomplete
from socketio import Client
from socketio._types import DataType, TransportType
from typing_extensions import Self

class SimpleClient:
    client_class: ClassVar[type[Client]]
    client_args: tuple[Any, ...]
    client_kwargs: dict[str, Any]
    client: Client | None
    namespace: str
    connected_event: Event
    connected: bool
    input_event: Event
    input_buffer: list[list[Any]]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def connect(
        self,
        url: str,
        headers: dict[Incomplete, Incomplete] = ...,
        auth: Incomplete | None = ...,
        transports: TransportType | None = ...,
        namespace: str = ...,
        socketio_path: str = ...,
        wait_timeout: int = ...,
    ) -> None: ...
    @property
    def sid(self) -> str | None: ...
    @property
    def transport(self) -> TransportType | Literal[""]: ...
    def emit(
        self, event: str, data: DataType | tuple[DataType, ...] | None = ...
    ) -> None: ...
    def call(
        self,
        event: str,
        data: DataType | tuple[DataType, ...] | None = ...,
        timeout: int = ...,
    ) -> Incomplete | None: ...
    def receive(self, timeout: float | None = ...) -> list[Any]: ...
    def disconnect(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None: ...
