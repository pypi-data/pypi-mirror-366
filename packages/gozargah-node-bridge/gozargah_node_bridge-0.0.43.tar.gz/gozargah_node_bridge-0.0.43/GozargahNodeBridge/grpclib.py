import asyncio

from grpclib.client import Channel
from grpclib.config import Configuration
from grpclib.exceptions import GRPCError, StreamTerminatedError

from GozargahNodeBridge.common import service_pb2 as service
from GozargahNodeBridge.common import service_grpc
from GozargahNodeBridge.controller import NodeAPIError, Health
from GozargahNodeBridge.abstract_node import GozargahNode
from GozargahNodeBridge.utils import grpc_to_http_status


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

        try:
            self.channel = Channel(host=address, port=port, ssl=self.ctx, config=Configuration(_keepalive_timeout=10))
            self._client = service_grpc.NodeServiceStub(self.channel)
            self._metadata = {"x-api-key": api_key}
        except Exception as e:
            raise NodeAPIError(-1, f"Channel initialization failed: {str(e)}")

        self._node_lock = asyncio.Lock()

    def _close_chan(self):
        """Close gRPC channel"""
        if hasattr(self, "channel"):
            try:
                self.channel.close()
            except Exception:
                pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
        self._close_chan()

    def __del__(self):
        self._close_chan()

    async def _handle_error(self, error: Exception):
        """Convert gRPC errors to NodeAPIError with HTTP status codes."""
        if isinstance(error, asyncio.TimeoutError):
            raise NodeAPIError(-1, "Request timed out")
        elif isinstance(error, GRPCError):
            http_status = grpc_to_http_status(error.status)
            raise NodeAPIError(http_status, error.message)
        elif isinstance(error, StreamTerminatedError):
            raise NodeAPIError(-1, f"Stream terminated: {str(error)}")
        else:
            raise NodeAPIError(0, str(error))

    async def _handle_grpc_request(self, method, request, timeout=15):
        """Handle a gRPC request and convert errors to NodeAPIError."""
        try:
            return await asyncio.wait_for(method(request, metadata=self._metadata), timeout=timeout)
        except Exception as e:
            await self._handle_error(e)

    async def start(
        self,
        config: str,
        backend_type: service.BackendType,
        users: list[service.User],
        keep_alive: int = 0,
        ghather_logs: bool = True,
        timeout: int = 15,
    ) -> service.BaseInfoResponse | None:
        """Start the node"""
        health = await self.get_health()
        if health in (Health.BROKEN, Health.HEALTHY):
            await self.stop()
        elif health is Health.INVALID:
            raise NodeAPIError(code=-4, detail="Invalid node")

        req = service.Backend(type=backend_type, config=config, users=users, keep_alive=keep_alive)

        async with self._node_lock:
            info = await self._handle_grpc_request(
                method=self._client.Start,
                request=req,
                timeout=timeout,
            )
            tasks = [asyncio.create_task(self._check_node_health()), asyncio.create_task(self._sync_user())]
            if ghather_logs:
                tasks.append(asyncio.create_task(self._fetch_logs()))
            await self.connect(
                info.node_version,
                info.core_version,
                tasks,
            )
            return info

    async def stop(self, timeout: int = 10) -> None:
        """Stop the node"""
        if await self.get_health() is Health.NOT_CONNECTED:
            return

        async with self._node_lock:
            await self.disconnect()

            await self._handle_grpc_request(
                method=self._client.Stop,
                request=service.Empty(),
                timeout=timeout,
            )

    async def info(self, timeout: int = 10) -> service.BaseInfoResponse | None:
        return await self._handle_grpc_request(
            method=self._client.GetBaseInfo,
            request=service.Empty(),
            timeout=timeout,
        )

    async def get_system_stats(self, timeout: int = 10) -> service.SystemStatsResponse | None:
        return await self._handle_grpc_request(
            method=self._client.GetSystemStats,
            request=service.Empty(),
            timeout=timeout,
        )

    async def get_backend_stats(self, timeout: int = 10) -> service.BackendStatsResponse | None:
        return await self._handle_grpc_request(
            method=self._client.GetBackendStats,
            request=service.Empty(),
            timeout=timeout,
        )

    async def get_stats(
        self, stat_type: service.StatType, reset: bool = True, name: str = "", timeout: int = 10
    ) -> service.StatResponse | None:
        return await self._handle_grpc_request(
            method=self._client.GetStats,
            request=service.StatRequest(reset=reset, name=name, type=stat_type),
            timeout=timeout,
        )

    async def get_user_online_stats(self, email: str, timeout: int = 10) -> service.OnlineStatResponse | None:
        return await self._handle_grpc_request(
            method=self._client.GetUserOnlineStats,
            request=service.StatRequest(name=email),
            timeout=timeout,
        )

    async def get_user_online_ip_list(self, email: str, timeout: int = 10) -> service.StatsOnlineIpListResponse | None:
        return await self._handle_grpc_request(
            method=self._client.GetUserOnlineIpListStats,
            request=service.StatRequest(name=email),
            timeout=timeout,
        )

    async def sync_users(
        self, users: list[service.User], flush_queue: bool = False, timeout: int = 10
    ) -> service.Empty | None:
        if flush_queue:
            await self.flush_user_queue()

        async with self._node_lock:
            return await self._handle_grpc_request(
                method=self._client.SyncUsers,
                request=service.Users(users=users),
                timeout=timeout,
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
                async with self._client.GetLogs.open(metadata=self._metadata) as stream:
                    await stream.send_message(service.Empty())
                    while True:
                        log = await stream.recv_message()
                        if log is None:
                            continue
                        await self._logs_queue.put(log.detail)

            except Exception:
                await asyncio.sleep(10)
                continue

    async def _sync_user(self):
        while True:
            health = await self.get_health()
            if health == Health.BROKEN:
                await asyncio.sleep(10)
                continue
            elif health == Health.NOT_CONNECTED:
                return

            async with self._client.SyncUser.open(metadata=self._metadata) as stream:
                while True:
                    async with self._lock.reader_lock:
                        if self._user_queue is None or self._notify_queue is None:
                            return
                        user_task = asyncio.create_task(self._user_queue.get())
                        notify_task = asyncio.create_task(self._notify_queue.get())

                    try:
                        done, pending = await asyncio.wait(
                            [user_task, notify_task], return_when=asyncio.FIRST_COMPLETED
                        )
                    except asyncio.CancelledError:
                        user_task.cancel()
                        notify_task.cancel()
                        raise

                    for task in pending:
                        task.cancel()

                    if notify_task in done:
                        continue  # Handle notify event

                    if user_task in done:
                        user = user_task.result()
                        if user is None:
                            continue

                        try:
                            await stream.send_message(user)
                        except Exception:
                            break
