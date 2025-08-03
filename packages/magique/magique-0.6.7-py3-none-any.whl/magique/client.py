import typing as T
import asyncio
import uuid
import inspect
import websockets
import time

from .protocol import (
    ServiceInfo, InvokeServiceRequest, InvokeServiceResponse,
    InvokeFuture, GetFutureResultRequest, RegisterClientRequest,
)
from .utils.log import logger
from .ser import DefaultSerializer
from .utils.network import ws_connect
from .base import NetworkObject


class MagiqueError(Exception):
    pass


class MagiqueFutureError(MagiqueError):
    pass


class LoginError(MagiqueError):
    pass


class PyFunction:
    def __init__(self, func: T.Callable):
        self.func = func


class ServiceProxy:
    def __init__(
        self,
        server_proxy: T.Union["ServerProxy", "MultiConnectionServerProxy"],
        service_info: T.Optional[ServiceInfo] = None,
    ):
        self.server_proxy = server_proxy
        self.service_info = service_info

    async def ensure_connection(self):
        info = await self.server_proxy.ensure_connection(
            service_id_or_name=self.service_info.service_id,
        )
        self.service_info = info
        return info

    async def invoke(
        self,
        function_name: str,
        parameters: dict | None = None,
        return_future: bool = False,
    ) -> T.Any:
        invoke_id = str(uuid.uuid4())
        if parameters is None:
            parameters = {}
        reverse_callables = {}
        for k, v in parameters.items():
            if isinstance(v, T.Callable):
                reverse_callables[k] = v
                _parameters = inspect.signature(v).parameters
                parameters[k] = {
                    "reverse_callable": True,
                    "name": k,
                    "invoke_id": invoke_id,
                    "parameters": list(_parameters.keys()),
                    "is_async": inspect.iscoroutinefunction(v),
                }
            elif isinstance(v, PyFunction):
                parameters[k] = v.func  # pass the function object

        request = InvokeServiceRequest(
            client_id=self.server_proxy.client_id,
            service_id=self.service_info.service_id,
            function_name=function_name,
            parameters=parameters,
            return_future=return_future,
            invoke_id=invoke_id,
        )
        await self.ensure_connection()
        rid = await self.server_proxy.send(request.encode())
        response = None
        while True:
            resp = await self.server_proxy.recv(rid, auto_end=False)
            action = resp.get("action")
            logger.debug(f"Received action while waiting for result: {action}")
            if action == "reverse_invoke":
                await self.handle_reverse_invoke(resp, reverse_callables)
            else:
                if return_future:
                    response = InvokeFuture.decode(resp)
                else:
                    response = InvokeServiceResponse.decode(resp)
                    if resp.get("status") == "error":
                        raise MagiqueError(resp.get("message") or resp.get("result"))
                    response = response.result
                break
        await self.server_proxy.end_recv(rid)
        return response

    async def handle_reverse_invoke(self, request: dict, reverse_callables: dict):
        name = request["name"]
        parameters = request["parameters"]
        func = reverse_callables[name]
        try:
            if inspect.iscoroutinefunction(func):
                result = await func(**parameters)
            else:
                result = func(**parameters)
            status = "success"
        except Exception as e:
            result = str(e)
            status = "error"
        rid = await self.server_proxy.send({
            "action": "set_reverse_invoke_result",
            "result": result,
            "status": status,
            "reverse_invoke_id": request["reverse_invoke_id"],
            "service_id": request["service_id"],
        })
        resp = await self.server_proxy.recv(rid, auto_end=False)
        if resp.get("status") == "error":
            raise MagiqueError(resp.get("message"))

    async def fetch_service_info(self) -> ServiceInfo:
        request = {"action": "get_service_info"}
        if self.service_info is not None:
            request["name_or_id"] = self.service_info.service_id
        await self.ensure_connection()
        rid = await self.server_proxy.send(request)
        resp = await self.server_proxy.recv(rid)
        if resp.get("status") == "error":
            raise MagiqueError(resp.get("message"))
        response = ServiceInfo.decode(resp["service"])
        self.service_info = response
        return response

    async def fetch_future_result(self, future: InvokeFuture) -> T.Any:
        request = GetFutureResultRequest(future)
        await self.ensure_connection()
        rid = await self.server_proxy.send(request.encode())
        resp = await self.server_proxy.recv(rid)
        if resp.get("status") == "error":
            raise MagiqueFutureError(resp.get("message"))
        response = InvokeServiceResponse.decode(resp)
        return response.result

    async def close_connection(self):
        await self.server_proxy.close_connection()


class ServerProxy(NetworkObject):
    def __init__(
        self,
        url: str,
        serializer: DefaultSerializer | None = None,
        client_id: str | None = None,
    ):
        super().__init__(serializer or DefaultSerializer())
        self.url = url
        self.jwt = None
        self.client_id = client_id or str(uuid.uuid4())
        self._connection = None
        self._recv_queues = {}

    async def send(self, request: dict):
        """Please use this(send/recv) if you want receive response concurrently."""
        reqid = str(uuid.uuid4())
        request['request_id'] = reqid
        self._recv_queues[reqid] = asyncio.Queue()
        await self.send_message(self._connection, request)
        return reqid

    async def recv(self, req_id: str, auto_end: bool = True) -> dict:
        """Please use this(send/recv) if you want receive response concurrently."""
        while True:
            try:
                resp = await self.receive_message(self._connection)
                r_id = resp.pop("request_id")
                self._recv_queues[r_id].put_nowait(resp)
            except websockets.exceptions.ConcurrencyError:
                await asyncio.sleep(0.1)
                continue
            queue = self._recv_queues[req_id]
            resp = await queue.get()
            if auto_end:
                await self.end_recv(req_id)
            return resp

    async def end_recv(self, req_id: str):
        del self._recv_queues[req_id]

    async def register(self):
        request = RegisterClientRequest(client_id=self.client_id)
        websocket = await ws_connect(self.url)
        self._connection = websocket
        await self.send_message(websocket, request.encode())
        response = await self.receive_message(websocket)
        if response.get("status") == "error":
            raise MagiqueError(response.get("message"))
        logger.info(f"Connected to server at {self.url}")

    async def is_connected(self) -> bool:
        if self._connection is None:
            return False
        try:
            await self._connection.ping()
        except Exception:
            return False
        return True

    async def ensure_connection(
        self,
        retry_count: int = 3,
        retry_delay: float = 0.8,
        service_id_or_name: str | None = None,
    ):
        for _ in range(retry_count):
            if (await self.is_connected()):
                break
            try:
                await self.register()
                break
            except Exception:
                await asyncio.sleep(retry_delay)
        else:
            raise MagiqueError(
                f"Failed to connect to server during ensure_connection: {self.url}"
            )
        if service_id_or_name is not None:
            info = await self.get_service_info(service_id_or_name)
            return info
        else:
            return None

    async def list_services(self) -> T.List[ServiceInfo]:
        await self.ensure_connection()
        rid = await self.send(
            {"action": "get_services", "jwt": self.jwt}
        )
        response = await self.recv(rid)
        services = [
            ServiceInfo.decode(service)
            for service in response["services"]
        ]
        return services

    async def get_service_info(
        self,
        name_or_id: str,
        choice_strategy: T.Literal["random", "first"] = "first",
    ) -> ServiceInfo:
        request = {
            "action": "get_service_info",
            "name_or_id": name_or_id,
            "choice_strategy": choice_strategy,
            "jwt": self.jwt,
        }
        await self.ensure_connection()
        rid = await self.send(request)
        resp = await self.recv(rid)
        if resp.get("status") == "error":
            raise MagiqueError(resp.get("message"))
        info = ServiceInfo.decode(resp["service"])
        return info

    async def get_service(
        self,
        name_or_id: str,
        choice_strategy: T.Literal["random", "first"] = "first",
    ) -> ServiceProxy:
        info = await self.get_service_info(name_or_id, choice_strategy)
        proxy = ServiceProxy(self, info)
        return proxy

    async def ping(self):
        await self.ensure_connection()
        rid = await self.send({"action": "ping"})
        msg = await self.recv(rid)
        assert msg["message"] == "pong"

    async def login(self):
        if self.jwt is not None:
            logger.info("Already logged in.")
            return
        await self.ensure_connection()
        rid = await self.send({"action": "login"})
        msg = await self.recv(rid, auto_end=False)
        auth_url = msg["auth_url"]
        logger.info(f"Open this URL in your browser to log in:\n{auth_url}")
        msg = await self.recv(rid, auto_end=False)
        await self.end_recv(rid)
        if msg.get("status") == "error":
            raise LoginError(msg.get("message"))
        jwt = msg.get("jwt")
        self.jwt = jwt
        logger.info("Login successful!")

    async def close_connection(self):
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    def __repr__(self):
        return f"ServerProxy(url={self.url}, client_id={self.client_id})"


class MultiConnectionServerProxy(object):
    global_server_proxys: dict[str, ServerProxy] = {}

    def __init__(
        self,
        urls: T.List[str],
        client_id: str | None = None,
        use_global: bool = True,
        **kwargs,
    ):
        self.client_id = client_id or str(uuid.uuid4())
        self.use_global = use_global
        self._init_servers(urls, kwargs)
        self.active_server: ServerProxy | None = None
        self._request_id_to_server: dict[str, ServerProxy] = {}
    
    def _init_servers(self, urls: T.List[str], kwargs: dict):
        self.servers = []
        global_server_proxys = self.__class__.global_server_proxys
        for url in urls:
            if (not self.use_global) or (url not in global_server_proxys):
                server = ServerProxy(url, client_id=self.client_id, **kwargs)
                if self.use_global:
                    global_server_proxys[url] = server
            else:
                server = global_server_proxys[url]
            self.servers.append(server)

    async def send(self, request: dict):
        if self.active_server is None:
            raise MagiqueError("No active server")
        rid = await self.active_server.send(request)
        self._request_id_to_server[rid] = self.active_server
        return rid
    
    async def recv(self, req_id: str, auto_end: bool = True) -> dict:
        server = self._request_id_to_server[req_id]
        resp = await server.recv(req_id, auto_end)
        if auto_end:
            await self.end_recv(req_id)
        return resp

    async def end_recv(self, req_id: str):
        del self._request_id_to_server[req_id]

    async def ensure_connection(
        self,
        retry_count: int = 3,
        retry_delay: float = 0.5,
        service_id_or_name: str | None = None,
    ):
        if self.active_server is not None:
            if await self.active_server.is_connected():
                try:
                    info = await self.active_server.ensure_connection(
                        retry_count, retry_delay, service_id_or_name
                    )
                    return info
                except Exception:
                    self.active_server = None
            else:
                self.active_server = None

        async def try_connect(server: ServerProxy):
            start_time = time.time()
            try:
                info = await server.ensure_connection(
                    retry_count, retry_delay, service_id_or_name
                )
                delta = time.time() - start_time
                return delta, server, info
            except Exception as e:
                logger.debug(f"Failed to connect to server {server}: {e}")
                return None

        tasks = []
        for server in self.servers:
            tasks.append(asyncio.create_task(try_connect(server)))
        results = await asyncio.gather(*tasks)
        results = [r for r in results if r is not None]
        if len(results) == 0:
            error_msg = f"Failed to connect to any server: {self.servers}"
            if service_id_or_name is not None:
                error_msg += f"\nService ID or name: {service_id_or_name}"
            logger.error(error_msg)
            raise MagiqueError(error_msg)
        results.sort(key=lambda x: x[0])
        self.active_server = results[0][1]
        return results[0][2]

    async def ping(self):
        await self.ensure_connection()
        await self.active_server.ping()

    async def login(self):
        await self.ensure_connection()
        await self.active_server.login()

    async def list_services(self) -> T.List[ServiceInfo]:
        await self.ensure_connection()
        return await self.active_server.list_services()

    async def get_service_info(
        self,
        name_or_id: str,
        choice_strategy: T.Literal["random", "first"] = "first",
    ) -> ServiceInfo:
        await self.ensure_connection(service_id_or_name=name_or_id)
        return await self.active_server.get_service_info(name_or_id, choice_strategy)

    async def get_service(
        self,
        name_or_id: str,
        choice_strategy: T.Literal["random", "first"] = "first",
    ) -> ServiceProxy:
        info = await self.get_service_info(name_or_id, choice_strategy)
        proxy = ServiceProxy(self, info)
        return proxy

    async def is_connected(self) -> bool:
        return any(await server.is_connected() for server in self.servers)

    async def close_connection(self):
        for server in self.servers:
            await server.close_connection()


async def connect_to_server(
    url: str | list[str],
    **kwargs,
) -> ServerProxy:
    if isinstance(url, list) and len(url) == 1:
        url = url[0]
    if isinstance(url, str):
        server = ServerProxy(
            url,
            **kwargs,
        )
        await server.ensure_connection()
        return server
    else:
        server = MultiConnectionServerProxy(
            url,
            **kwargs,
        )
        await server.ensure_connection()
        return server

