import typing as T
import asyncio
import uuid
import functools
import traceback
import hashlib

import websockets
from funcdesc import parse_func
from executor.engine import Engine, EngineSetting
from executor.engine.launcher import launcher

from .utils.log import logger
from .protocol import (
    ServiceInfo, RegisterServiceRequest,
    InvokeServiceRequest, InvokeServiceResponse,
    InvokeFuture, GetFutureResultRequest, FutureResponse,
)
from .ser import DefaultSerializer
from .utils.network import ws_connect
from .base import NetworkObject

if T.TYPE_CHECKING:
    from .client import ServiceProxy


class ReverseCallable(NetworkObject):
    def __init__(
        self,
        websocket,
        name: str,
        client_id: str,
        service_id: str,
        invoke_id: str,
        invoke_futures: dict[str, asyncio.Future],
        parameters: list[str] | None = None,
        is_async: bool = True,
        serializer: DefaultSerializer | None = None,
    ):
        super().__init__(serializer or DefaultSerializer())
        self.name = name
        self.client_id = client_id
        self.invoke_id = invoke_id
        self.service_id = service_id
        self.parameters = parameters
        self.is_async = is_async
        self.websocket = websocket
        self._invoke_futures = invoke_futures

    async def invoke(self, params: dict):
        reverse_invoke_id = str(uuid.uuid4())
        self._invoke_futures[reverse_invoke_id] = asyncio.Future()
        logger.debug(f"Sending reverse invoke request: {self.name} with params: {params}")
        await self.send_message(self.websocket, {
            "action": "reverse_invoke",
            "name": self.name,
            "invoke_id": self.invoke_id,
            "client_id": self.client_id,
            "service_id": self.service_id,
            "parameters": params,
            "reverse_invoke_id": reverse_invoke_id,
        })
        resp = await self._invoke_futures[reverse_invoke_id]
        return resp["result"]

    def __call__(self, *args, **kwargs):
        _params = {}
        if self.parameters:
            for i, v in enumerate(self.parameters):
                if i < len(args):
                    _params[v] = args[i]
        _params.update(kwargs)
        return self.invoke(_params)

    @property
    def __name__(self):
        return self.name


class MagiqueWorker(NetworkObject):
    def __init__(
        self,
        service_name: str,
        server_url: list[str] | str = ["wss://magique.spateo.aristoteleo.com/ws"],
        serializer: T.Optional[DefaultSerializer] = None,
        engine_setting: T.Optional[EngineSetting] = None,
        need_auth: bool = False,
        id_hash: str | None = None,
        max_reconnection_attempts: int = 20,
        base_reconnection_delay: float = 1,
        max_reconnection_delay: float = 30,
        description: str = "",
        visible: bool = True,
    ):
        super().__init__(serializer or DefaultSerializer())
        if isinstance(server_url, str):
            self.servers = [server_url]
        else:
            self.servers = server_url
        self.service_name = service_name
        self.description = description
        self.functions = {}
        self.client_registry = {}
        if id_hash:
            self.service_id = hashlib.sha256(id_hash.encode()).hexdigest()
        else:
            self.service_id = str(uuid.uuid4())
        self.engine = Engine(setting=engine_setting)
        self._invokeid_to_jobid = {}
        self.need_auth = need_auth
        self.max_reconnection_attempts = max_reconnection_attempts
        self.base_reconnection_delay = base_reconnection_delay
        self.max_reconnection_delay = max_reconnection_delay
        self.connected = False
        self.visible = visible
        self._reverse_invoke_futures: dict[str, asyncio.Future] = {}
        self.registered_servers = set()

    async def handle_request(self, request: dict, websocket):
        logger.info(f"Received request:\n{request}")
        action = request.get("action")
        if action == "invoke_service":
            await self.handle_invoke_function(request, websocket)
        elif action == "get_service_info":
            service_info = self.get_service_info()
            resp = {
                "status": "success",
                "service": service_info.encode(),
            }
            await self.send_message(websocket, resp)
        elif action == "get_future_result":
            await self.handle_get_future_result(request, websocket)
        elif action == "ping":
            response = {"status": "success", "message": "pong"}
            await self.send_message(websocket, response)
        elif action == "auth":
            await self.handle_auth(request, websocket)
        elif action == "set_reverse_invoke_result":
            await self.handle_set_reverse_invoke_result(request)
        else:
            logger.error(f"Unknown action: {action}")

    async def handle_set_reverse_invoke_result(self, request: dict):
        reverse_invoke_id = request["reverse_invoke_id"]
        future = self._reverse_invoke_futures[reverse_invoke_id]
        future.set_result(request)

    async def handle_invoke_function(self, request: dict, websocket):
        invoke_request = InvokeServiceRequest.decode(request)
        if invoke_request.function_name not in self.functions:
            await self.send_message(
                websocket,
                InvokeServiceResponse(
                    invoke_id=invoke_request.invoke_id,
                    status="error",
                    result="Function not found",
                ).encode(),
            )
            return
        function, job_type = self.functions[invoke_request.function_name]
        f_launcher = launcher(
            function, engine=self.engine, job_type=job_type,
            async_mode=True)
        parameters = await self.resolve_parameters(invoke_request.parameters)
        if "__client_id__" in function.__code__.co_varnames:
            # inject client_id into the function
            parameters["__client_id__"] = invoke_request.client_id
        # process reverse callables
        for k, v in parameters.items():
            if isinstance(v, dict) and v.get("reverse_callable"):
                parameters[k] = ReverseCallable(
                    websocket, v["name"],
                    invoke_request.client_id, invoke_request.service_id,
                    v["invoke_id"], self._reverse_invoke_futures,
                    v.get("parameters"), v.get("is_async", True),
                )
        job = await f_launcher.submit(**parameters)
        self._invokeid_to_jobid[invoke_request.invoke_id] = job.id
        if invoke_request.return_future:
            future = InvokeFuture(
                invoke_id=invoke_request.invoke_id,
                service_id=self.service_id,
            )
            future_response = FutureResponse(future)
            await self.send_message(websocket, future_response.encode())
        else:
            asyncio.create_task(self._wait_and_send_job_after_completion(
                job, websocket, invoke_request.invoke_id
            ))

    async def handle_get_future_result(self, request: dict, websocket):
        get_future_result_request = GetFutureResultRequest.decode(request)
        future = get_future_result_request.future
        job_id = self._invokeid_to_jobid.get(future.invoke_id)
        if job_id is None:
            logger.error(f"Job not found: id={job_id}")
            response = InvokeServiceResponse(
                invoke_id=future.invoke_id,
                status="error",
                result="Job not found",
            )
            await self.send_message(websocket, response.encode())
            return
        job = self.engine.jobs.get_job_by_id(job_id)
        asyncio.create_task(self._wait_and_send_job_after_completion(
            job, websocket, future.invoke_id
        ))

    async def _wait_and_send_job_after_completion(self, job, websocket, invoke_id):
        try:
            await job.join()
            if job.status == "done":
                result = job.result()
                status = "success"
            else:
                e = job.exception()
                result = "\n".join(traceback.format_exception(e))
                status = "error"

            response_data = InvokeServiceResponse(
                invoke_id=invoke_id,
                status=status,
                result=result,
            ).encode()
            await self.send_message(websocket, response_data)
        except websockets.exceptions.ConnectionClosed:
            logger.warning(
                f"Connection closed for invoke_id {invoke_id} before job result could be sent."
            )
        except Exception as e:
            logger.error(
                f"Error waiting for job or sending result for invoke_id {invoke_id}: {e}\n"
                f"{traceback.format_exc()}"
            )
            # Attempt to send an error response if the connection is still open
            if not isinstance(e, websockets.exceptions.ConnectionClosed) and websocket.open:
                try:
                    error_response_data = InvokeServiceResponse(
                        invoke_id=invoke_id,
                        status="error",
                        result=f"Server error processing job: {str(e)}",
                    ).encode()
                    await self.send_message(websocket, error_response_data)
                except Exception as send_exc:
                    logger.error(
                        f"Failed to send error notification for invoke_id {invoke_id} "
                        f"after an initial error: {send_exc}"
                    )

    async def resolve_parameters(self, parameters: dict):
        for key, value in parameters.items():
            if isinstance(value, InvokeFuture):
                # wait for the future result
                future = value
                if future.service_id != self.service_id:
                    for server_url in self.servers:
                        logger.info(
                            f"Future from other service: id={future.service_id}"
                            f"Connecting to the server at {server_url}"
                        )
                        try:
                            service = await self.get_another_service(server_url, future.service_id)
                            result = await service.fetch_future_result(future)
                            break
                        except Exception as e:
                            logger.error(f"Error getting another service from {server_url}: {e}")
                    else:
                        raise RuntimeError(f"Failed to get another service: {e}")
                else:
                    job_id = self._invokeid_to_jobid.get(future.invoke_id)
                    if job_id is None:
                        logger.error(f"Job not found: id={job_id}")
                        raise ValueError(f"Job not found: id={job_id}")
                    job = self.engine.jobs.get_job_by_id(job_id)
                    await job.join()
                    if job.status == "done":
                        result = job.result()
                    else:
                        raise RuntimeError(f"Job failed: id={job_id}")
                parameters[key] = result
        return parameters

    async def get_another_service(self, server_url: str, service_id: str) -> "ServiceProxy":
        from .client import connect_to_server
        server = await connect_to_server(server_url)
        service = await server.get_service(service_id)
        return service

    def get_service_info(self):
        service_info = ServiceInfo(
            service_name=self.service_name,
            service_id=self.service_id,
            description=self.description,
            functions_description={
                name: parse_func(func)
                for name, (func, _) in self.functions.items()
            },
            need_auth=self.need_auth,
            visible=self.visible,
        )
        return service_info

    async def register_to_server(self, server_url: str, websocket):
        logger.info(f"Connected to the server at {server_url}")
        service_info = self.get_service_info()
        registration = RegisterServiceRequest(service_info).encode()
        logger.info(f"Sending registration request:\n{registration}")
        await self.send_message(websocket, registration)
        response = await self.receive_message(websocket)
        logger.info(f"Registration response:\n{response}")
        if response.get("status") == "success":
            logger.info(f"Registration successful")
        else:
            raise RuntimeError(f"Registration failed: {response.get('message')}")

    async def handle_server_requests(self, websocket):
        while True:
            request = await self.receive_message(websocket)
            await self.handle_request(request, websocket)

    async def handle_client_request(self, websocket):
        try:
            while True:
                request = await self.receive_message(websocket)
                action = request.get("action")
                if action == "register_client":
                    asyncio.create_task(self.handle_register_client(request, websocket))
                else:
                    logger.error(f"Unknown action: {action}")
        except websockets.exceptions.ConnectionClosed:
            logger.debug("Client connection closed")

    async def register_and_handle_server_requests(
            self,
            server_url: str,
            after_register: T.Optional[T.Callable[[object], T.Awaitable]] = None):
        max_retries = self.max_reconnection_attempts
        base_delay = self.base_reconnection_delay
        max_delay = self.max_reconnection_delay
        retry_count = 0

        while True:
            try:
                logger.info(f"Connecting to server at {server_url}")
                async with ws_connect(server_url) as websocket:
                    retry_count = 0
                    await self.register_to_server(server_url, websocket)
                    if after_register:
                        await after_register(websocket)
                    self.registered_servers.add(server_url)
                    await self.handle_server_requests(websocket)
            except Exception as e:
                logger.debug(f"Error connecting to server {server_url}: {e}")
                logger.info("Current registered servers: " + str(self.registered_servers))
                traceback.print_exc()
                self.registered_servers.discard(server_url)
                retry_count += 1
                if max_retries > 0 and retry_count > max_retries:
                    logger.debug(
                        f"Maximum reconnection to {server_url} attempts ({max_retries}) "
                        "reached. Giving up.")
                    break
                # exponential backoff
                delay = min(base_delay * (2 ** (retry_count - 1)), max_delay)
                if max_retries > 0:
                    at = f"attempt {retry_count}/{max_retries}"
                else:
                    at = "unlimited"
                logger.debug(
                    f"Connection to server {server_url} lost: {e}. "
                    f"Reconnecting to {server_url} in {delay:.2f} seconds ({at})..."
                )
                await asyncio.sleep(delay)

    async def run(self, after_register: T.Optional[T.Callable[[object], T.Awaitable]] = None):
        coroutines = []
        for server_url in self.servers:
            coroutines.append(self.register_and_handle_server_requests(server_url, after_register))
        await asyncio.gather(*coroutines)

    def register(self, function: T.Optional[T.Callable] = None, **kwargs):
        if function is None:
            return functools.partial(self.register, **kwargs)
        job_type = kwargs.get("job_type", "local")
        self.functions[function.__name__] = (function, job_type)
        return function

    def register_action(self, action: str):
        def _register_action(
                function: T.Callable[[dict, object], T.Coroutine]):
            self.actions[action] = function
            return function
        return _register_action

    async def handle_auth(self, request: dict, websocket):
        user_info = request.get("user_info")
        auth_id = request.get("auth_id")
        resp = {
            "action": "worker_auth_response",
            "status": "failed",
            "auth_id": auth_id,
        }
        if self.auth_function(user_info):
            resp["status"] = "success"
        await self.send_message(websocket, resp)

    def auth_function(self, user_info: dict) -> bool:
        return True

    def register_auth(self, function: T.Callable[[dict], bool]):
        self.auth_function = function
        return function


def main():
    worker = MagiqueWorker("test_worker")
    asyncio.run(worker.run())


if __name__ == "__main__":
    main()
