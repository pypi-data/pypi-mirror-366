import asyncio

import httpx
from google.protobuf.message import Message, DecodeError

from GozargahNodeBridge.controller import NodeAPIError, Health
from GozargahNodeBridge.common import service_pb2 as service
from GozargahNodeBridge.abstract_node import GozargahNode


class Node(GozargahNode):
    def __init__(
        self,
        address: str,
        port: int,
        server_ca: str,
        api_key: str,
        extra: dict | None = None,
        max_logs: int = 1000,
    ):
        super().__init__(server_ca, api_key, extra, max_logs)

        url = f"https://{address.strip('/')}:{port}/"

        self._client = httpx.AsyncClient(
            http2=True,
            verify=self.ctx,
            headers={"Content-Type": "application/x-protobuf", "x-api-key": api_key},
            base_url=url,
            timeout=httpx.Timeout(None),
        )

        self._node_lock = asyncio.Lock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
        await self._client.aclose()

    def _serialize_protobuf(self, proto_message: Message) -> bytes:
        """Serialize a protobuf message to bytes."""
        return proto_message.SerializeToString()

    def _deserialize_protobuf(self, proto_class: type[Message], data: bytes) -> Message:
        """Deserialize bytes into a protobuf message."""
        proto_instance = proto_class()
        try:
            proto_instance.ParseFromString(data)
        except DecodeError as e:
            raise NodeAPIError(code=-2, detail=f"Error deserialising protobuf: {e}")
        return proto_instance

    def _handle_error(self, error: Exception):
        if isinstance(error, httpx.RemoteProtocolError):
            raise NodeAPIError(code=-1, detail=f"Server closed connection: {error}")
        elif isinstance(error, httpx.HTTPStatusError):
            raise NodeAPIError(code=error.response.status_code, detail=f"HTTP error: {error.response.text}")
        elif isinstance(error, httpx.ConnectError) or isinstance(error, httpx.ReadTimeout):
            raise NodeAPIError(code=-1, detail=f"Connection error: {error}")
        else:
            raise NodeAPIError(0, str(error))

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        timeout: int,
        proto_message: Message = None,
        proto_response_class: type[Message] = None,
    ) -> Message:
        """Handle common REST API call logic with protobuf support (async)."""
        request_data = None

        if proto_message:
            request_data = self._serialize_protobuf(proto_message)

        try:
            response = await self._client.request(
                method=method,
                url=endpoint,
                content=request_data,
                timeout=timeout,
            )
            response.raise_for_status()

            if proto_response_class:
                return self._deserialize_protobuf(proto_response_class, response.content)
            return response.content

        except Exception as e:
            self._handle_error(e)

    async def start(
        self,
        config: str,
        backend_type: service.BackendType,
        users: list[service.User],
        keep_alive: int = 0,
        ghather_logs: bool = True,
        timeout: int = 15,
    ):
        health = await self.get_health()
        if health in (Health.BROKEN, Health.HEALTHY):
            await self.stop()
        elif health is Health.INVALID:
            raise NodeAPIError(code=-4, detail="Invalid node")

        async with self._node_lock:
            response = await self._make_request(
                method="POST",
                endpoint="start",
                timeout=timeout,
                proto_message=service.Backend(type=backend_type, config=config, users=users, keep_alive=keep_alive),
                proto_response_class=service.BaseInfoResponse,
            )

            tasks = [asyncio.create_task(self._check_node_health()), asyncio.create_task(self._sync_user())]
            if ghather_logs:
                tasks.append(asyncio.create_task(self._fetch_logs()))
            await self.connect(
                response.node_version,
                response.core_version,
                tasks,
            )

        return response

    async def stop(self, timeout: int = 10) -> None:
        if await self.get_health() is Health.NOT_CONNECTED:
            return
        async with self._node_lock:
            await self.disconnect()
            await self._make_request(method="PUT", endpoint="stop", timeout=timeout)

    async def info(self, timeout: int = 10) -> service.BaseInfoResponse | None:
        return await self._make_request(
            method="GET", endpoint="info", timeout=timeout, proto_response_class=service.BaseInfoResponse
        )

    async def get_system_stats(self, timeout: int = 10) -> service.SystemStatsResponse | None:
        return await self._make_request(
            method="GET", endpoint="stats/system", timeout=timeout, proto_response_class=service.SystemStatsResponse
        )

    async def get_backend_stats(self, timeout: int = 10) -> service.BackendStatsResponse | None:
        return await self._make_request(
            method="GET", endpoint="stats/backend", timeout=timeout, proto_response_class=service.BackendStatsResponse
        )

    async def get_stats(
        self, stat_type: service.StatType, reset: bool = True, name: str = "", timeout: int = 10
    ) -> service.StatResponse | None:
        return await self._make_request(
            method="GET",
            endpoint="stats",
            timeout=timeout,
            proto_message=service.StatRequest(reset=reset, name=name, type=stat_type),
            proto_response_class=service.StatResponse,
        )

    async def get_user_online_stats(self, email: str, timeout: int = 10) -> service.OnlineStatResponse | None:
        return await self._make_request(
            method="GET",
            endpoint="stats/user/online",
            timeout=timeout,
            proto_message=service.StatRequest(name=email),
            proto_response_class=service.OnlineStatResponse,
        )

    async def get_user_online_ip_list(self, email: str, timeout: int = 10) -> service.StatsOnlineIpListResponse | None:
        return await self._make_request(
            method="GET",
            endpoint="stats/user/online_ip",
            timeout=timeout,
            proto_message=service.StatRequest(name=email),
            proto_response_class=service.StatsOnlineIpListResponse,
        )

    async def sync_users(
        self, users: list[service.User], flush_queue: bool = False, timeout: int = 10
    ) -> service.Empty | None:
        if flush_queue:
            await self.flush_user_queue()

        async with self._node_lock:
            return await self._make_request(
                method="POST",
                endpoint="users/sync",
                timeout=timeout,
                proto_message=service.Users(users=users),
                proto_response_class=service.Empty,
            )

    async def _check_node_health(self):
        while True:
            last_health = await self.get_health()

            try:
                await self.get_backend_stats()
                if last_health != Health.HEALTHY:
                    await self.set_health(Health.HEALTHY)
            except Exception:
                if last_health != Health.BROKEN:
                    await self.set_health(Health.BROKEN)

            await asyncio.sleep(10)

    async def _fetch_logs(self):
        while True:
            health = await self.get_health()
            if health == Health.BROKEN:
                await asyncio.sleep(10)
                continue
            elif health == Health.NOT_CONNECTED:
                return

            try:
                async with self._client.stream("GET", "/logs", timeout=None) as response:
                    buffer = b""

                    async for chunk in response.aiter_bytes():
                        buffer += chunk

                        while b"\n" in buffer:
                            line, buffer = buffer.split(b"\n", 1)
                            line = line.decode().strip()

                            if line:
                                if self._logs_queue:
                                    await self._logs_queue.put(line)

            except Exception:
                await asyncio.sleep(10)
                continue

    async def _sync_user(self) -> None:
        while True:
            health = await self.get_health()

            if health == Health.BROKEN:
                await asyncio.sleep(10)
                continue
            elif health == Health.NOT_CONNECTED:
                return

            async with self._lock.reader_lock:
                if self._user_queue is None or self._notify_queue is None:
                    return

                user_task = asyncio.create_task(self._user_queue.get())
                notify_task = asyncio.create_task(self._notify_queue.get())

            try:
                # Wait for first completed operation
                done, pending = await asyncio.wait([user_task, notify_task], return_when=asyncio.FIRST_COMPLETED)

            except asyncio.CancelledError:
                # Cleanup if task is cancelled
                user_task.cancel()
                notify_task.cancel()
                return

            # Cancel pending tasks to avoid leaks
            for task in pending:
                task.cancel()

            if notify_task in done:
                continue

            # Handle UserChan message
            if user_task in done:
                user = user_task.result()
                if user is None:
                    continue

                try:
                    await self._make_request(
                        method="PUT",
                        endpoint="user/sync",
                        timeout=10,
                        proto_message=user,
                        proto_response_class=service.Empty,
                    )
                except Exception:
                    await asyncio.sleep(10)
                    continue
