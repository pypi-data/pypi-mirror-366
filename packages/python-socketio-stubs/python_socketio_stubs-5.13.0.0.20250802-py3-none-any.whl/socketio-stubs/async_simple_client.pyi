import asyncio
import types
from typing import Any, ClassVar, Literal

from _typeshed import Incomplete
from socketio import Client
from socketio._types import DataType, TransportType
from socketio.async_client import AsyncClient
from typing_extensions import Self

class AsyncSimpleClient:
    client_class: ClassVar[type[AsyncClient]]
    client_args: tuple[Any, ...]
    client_kwargs: dict[str, Any]
    client: Client | None
    namespace: str
    connected_event: asyncio.Event
    connected: bool
    input_event: asyncio.Event
    input_buffer: list[list[Any]]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    async def connect(
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
    async def emit(
        self, event: str, data: DataType | tuple[DataType, ...] | None = ...
    ) -> None: ...
    async def call(
        self,
        event: str,
        data: DataType | tuple[DataType, ...] | None = ...,
        timeout: int = ...,
    ) -> Incomplete | None: ...
    async def receive(self, timeout: float | None = ...) -> list[Any]: ...
    async def disconnect(self) -> None: ...
    async def __aenter__(self) -> Self: ...
    async def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None: ...
