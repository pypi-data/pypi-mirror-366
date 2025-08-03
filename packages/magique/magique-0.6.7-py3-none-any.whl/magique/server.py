import asyncio
import sys
import uuid
from collections import defaultdict
import typing as T

from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fire import Fire

from .version import __version__
from .utils.log import logger
from .protocol import (
    ServiceInfo, RegisterServiceRequest,
    InvokeServiceRequest, InvokeServiceResponse,
    GetFutureResultRequest, FutureResponse,
    ClientInfo, RegisterClientRequest,
)
from .ser import DefaultSerializer
from .auth import AuthManager


class MagiqueServer:
    def __init__(
        self, host: str = "localhost", port: int = 8765,
        serializer: T.Optional[DefaultSerializer] = None,
    ):
        self.host = host
        self.port = port
        self.app = FastAPI(title="Magique Server")
        self.service_registry: T.Dict[str, ServiceInfo] = {}
        self.client_registry: T.Dict[str, ClientInfo] = {}
        self.pending_requests: T.Dict[str, asyncio.Future] = defaultdict(
            asyncio.Future
        )
        self.auth = AuthManager(
            redirect_uri=f"http://{host}:{port}/auth_callback"
        )
        self._setup_routes()
        self.serializer = serializer or DefaultSerializer()
        self.worker_auth_futures: T.Dict[str, asyncio.Future] = {}
        self._invokeid_to_request_id: T.Dict[str, str] = {}

    async def send_message(self, websocket: WebSocket, message: dict):
        ser_message = self.serializer.serialize(message, pack_inner=False)
        await websocket.send_bytes(ser_message)

    async def receive_message(self, websocket: WebSocket) -> dict:
        message = await websocket.receive_bytes()
        return self.serializer.deserialize(message, unpack_inner=False)

    def _setup_routes(self):
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            try:
                await self._handle_register(websocket)
            except WebSocketDisconnect:
                # Clean up any services registered by this websocket
                self._cleanup_disconnected_service(websocket)

        self.app.get("/auth_callback")(self.auth.auth_callback)
        
        # Add static files and test page routes
        import os
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        if os.path.exists(static_dir):
            self.app.mount("/static", StaticFiles(directory=static_dir), name="static")
        
        @self.app.get("/test")
        async def websocket_test_page():
            """WebSocket test page"""
            static_file = os.path.join(os.path.dirname(__file__), "static", "websocket_test.html")
            if os.path.exists(static_file):
                return FileResponse(static_file)
            else:
                return {"error": "Test page not found"}
        
        @self.app.get("/")
        async def root():
            """Root path with server info"""
            return {"message": "Magique Server is running", "version": __version__}

    def _cleanup_disconnected_service(self, websocket: WebSocket):
        # Remove any services associated with the disconnected websocket
        disconnected_services = [
            service_id for service_id, info in self.service_registry.items()
            if info.websocket == websocket
        ]
        for service_id in disconnected_services:
            del self.service_registry[service_id]
            logger.info(
                f"Service {service_id} disconnected and removed from registry")

    async def _handle_register(self, websocket: WebSocket) -> None:
        try:
            request = await self.receive_message(websocket)
            action = request.get("action")
            logger.info(
                f"Received action: {action} from {websocket.client.host}")
            response: T.Optional[dict] = None

            # handle actions from the client or worker's registration
            if action == "register_client":
                response = await self.handle_register_client(request, websocket)
            elif action == "register_service":  # from worker
                response = await self.handle_register_service(request, websocket)
            else:
                response = {
                    "status": "error",
                    "message": "Unknown action."
                }

            if response:
                await self.send_message(websocket, response)

        except WebSocketDisconnect as e:
            raise e
        except Exception as e:
            logger.error(f"Error handling websocket:\n{e}")
            import traceback
            traceback.print_exc()

    async def handle_login(self, websocket: WebSocket, request_id: str) -> dict:
        auth_url = self.auth.get_auth_url()
        await self.send_message(websocket, {"auth_url": auth_url, "request_id": request_id})
        timeout = self.auth.login_timeout  # seconds
        time_delta = 0.5
        while True:
            # wait for the user to login
            if self.auth._auth_response is not None:
                break

            await asyncio.sleep(time_delta)
            timeout -= time_delta
            if timeout <= 0:
                logger.error("Login timeout.")
                return {"status": "error", "message": "Login timeout."}
        try:
            await self.auth.fetch_token()
            user_info = await self.auth.get_user_info()
            logger.info(f"User logged in:\n{user_info}")
        except Exception as e:
            logger.error(f"Failed to fetch token or get user info:\n{e}")
            return {"status": "error", "message": str(e)}
        jwt = self.auth.create_jwt(user_info)
        return {"status": "success", "jwt": jwt}

    async def handle_client_requests(self, request: dict, websocket):
        action = request.get("action")
        logger.debug(f"Received action: {action} from client.")
        request_id = request.get("request_id")
        if action == "invoke_service":
            self._invokeid_to_request_id[request["invoke_id"]] = request_id
            resp = await self.handle_invoke_service(request)
        elif action == "get_services":
            resp = await self.handle_get_services(request)
        elif action == "get_future_result":
            resp = await self.handle_get_future_result(request)
        elif action == "ping":
            resp = {"status": "success", "message": "pong"}
        elif action == "login":
            resp = await self.handle_login(websocket, request_id)
        elif action == "get_service_info":
            resp = await self.handle_get_service_info(request)
        elif action == "set_reverse_invoke_result":
            resp = await self.handle_set_reverse_invoke_result(request)
        else:
            resp = {
                "status": "error",
                "message": f"Unknown action: {action}",
            }
        if resp is not None:
            resp["request_id"] = request_id
            await self.send_message(websocket, resp)

    async def handle_register_client(self, request: dict, websocket):
        try:
            register_request = RegisterClientRequest.decode(request)
            client_info = register_request.client_info
            client_info.websocket = websocket
            self.client_registry[client_info.client_id] = client_info
        except Exception as e:
            logger.error(f"Error registering client:\n{e}")
            return {"status": "error", "message": str(e)}
        resp = {
            "status": "success",
            "message": "Client registered successfully.",
        }
        await self.send_message(websocket, resp)
        while True:
            # loop for listening the client's message
            try:
                request = await self.receive_message(websocket)
                asyncio.create_task(self.handle_client_requests(request, websocket))
            except WebSocketDisconnect:
                logger.info("Websocket disconnected")
                if client_info.client_id in self.client_registry:
                    del self.client_registry[client_info.client_id]
                break
            except Exception as e:
                logger.error(f"Error handling websocket from {client_info.client_id}:\n{e}")
                import traceback
                traceback.print_exc()

    async def handle_register_service(self, request: dict, websocket):
        try:
            register_request = RegisterServiceRequest.decode(request)
            service_info = register_request.service_info
            service_info.websocket = websocket
        except Exception as e:
            logger.error(f"Error registering service:\n{e}")
            return {"status": "error", "message": str(e)}
        if service_info.service_id in self.service_registry:
            logger.warning(
                f"Service '{service_info.service_name}'"
                f"({service_info.service_id}) already registered. "
                f"Overwriting the existing service."
            )
        self.service_registry[service_info.service_id] = service_info
        resp = {
            "status": "success",
            "message": (
                f"Service '{service_info.service_name}'"
                f"({service_info.service_id}) registered successfully."
            ),
        }
        await self.send_message(websocket, resp)

        while True:
            # loop for listening the worker's message
            try:
                request = await self.receive_message(websocket)
                # handle actions from worker
                action = request.get("action")
                logger.debug(
                    f"Received action from worker: "
                    f"{service_info.service_name}({service_info.service_id}), "
                    f"action: {action}")
                if action == "worker_response":
                    await self.handle_worker_response(request)
                elif action == "future_response":
                    await self.handle_future_response(request)
                elif action == "worker_auth_response":
                    await self.handle_worker_auth_response(request)
                elif action == "reverse_invoke":
                    await self.handle_reverse_invoke(request)
            except WebSocketDisconnect:
                logger.info("Websocket disconnected")
                # unregister services
                service_info.websocket = None
                if service_info.service_id in self.service_registry:
                    del self.service_registry[service_info.service_id]
                break
            except Exception as e:
                logger.error(f"Error handling websocket from {service_info.service_name}:\n{e}")
                import traceback
                traceback.print_exc()

    async def handle_reverse_invoke(self, request: dict) -> None:
        client_id = request["client_id"]
        request_id = self._invokeid_to_request_id[request["invoke_id"]]
        if client_id in self.client_registry:
            client_websocket = self.client_registry[client_id].websocket
            request["request_id"] = request_id
            logger.debug(f"Sending reverse invoke request to client: {client_id}")
            await self.send_message(client_websocket, request)
            logger.debug(f"Sent reverse invoke request to client: {client_id}")
        else:
            logger.error(f"Client websocket not found for client_id: {client_id}")

    async def handle_worker_auth_response(self, request: dict) -> None:
        auth_id = request.get("auth_id")
        success = request.get("status") == "success"
        if auth_id in self.worker_auth_futures:
            f = self.worker_auth_futures[auth_id]
            f.set_result(success)
            del self.worker_auth_futures[auth_id]

    async def handle_auth(self, service, user_info) -> None:
        auth_id = str(uuid.uuid4())
        await self.send_message(
            service.websocket,
            {
                "action": "auth",
                "user_info": user_info,
                "auth_id": auth_id,
            }
        )
        f = self.worker_auth_futures[auth_id] = asyncio.Future()
        success = await f
        return success

    async def handle_get_services(self, request: dict) -> dict:
        jwt = request.get("jwt")
        user_info = None
        if jwt is not None:
            user_info = self.auth.decode_jwt(jwt)
            logger.info(f"User info:\n{user_info}")
        services = list(self.service_registry.values())
        encoded_services = []
        for service in services:
            if not service.visible:
                continue
            if service.need_auth:
                if user_info is not None:
                    success = await self.handle_auth(service, user_info)
                    if success:
                        encoded_services.append(service.encode())
            else:
                encoded_services.append(service.encode())
        return {
            "status": "success",
            "services": encoded_services,
        }

    async def handle_get_service_info(self, request: dict) -> dict:
        name_or_id = request.get("name_or_id")
        services_found = []
        for service_info in self.service_registry.values():
            if service_info.service_id == name_or_id or service_info.service_name == name_or_id:
                services_found.append(service_info)
        if len(services_found) == 0:
            return {
                "status": "error",
                "message": f"Service '{name_or_id}' not found.",
            }
        else:
            logger.info(f"Found {len(services_found)} services for '{name_or_id}'")
            strategy = request.get("choice_strategy", "first")
            if strategy == "first":
                service = services_found[0]
            elif strategy == "random":
                import random
                service = random.choice(services_found)
            else:
                logger.error(f"Invalid choice strategy: {strategy}")
                return {
                    "status": "error",
                    "message": f"Invalid choice strategy: {strategy}",
                }

            # deal with auth
            if service.need_auth:
                jwt = request.get("jwt")
                if jwt is None:
                    return {
                        "status": "error",
                        "message": "Service requires authentication but no JWT provided.",
                    }
                user_info = self.auth.decode_jwt(jwt)
                if user_info is None:
                    return {
                        "status": "error",
                        "message": "Invalid JWT.",
                    }
                success = await self.handle_auth(service, user_info)
                if not success:
                    return {
                        "status": "error",
                        "message": "Authentication failed.",
                    }
            logger.info(f"Selected service: {service} with strategy: {strategy}")
        return {
            "status": "success",
            "service": service.encode(),
        }

    async def handle_set_reverse_invoke_result(self, request: dict) -> None:
        try:
            service_info = self.service_registry[request["service_id"]]
            service_socket = service_info.websocket
            await self.send_message(service_socket, request)
        except Exception as e:
            logger.error(f"Error setting reverse invoke result for service {request['service_id']}:\n{e}")
            return {
                "status": "error",
                "message": str(e),
            }
        return {
            "status": "success",
        }

    async def handle_invoke_service(self, request: dict) -> dict:
        invoke_request = InvokeServiceRequest.decode(request)
        if invoke_request.service_id in self.service_registry:
            service_info = self.service_registry[invoke_request.service_id]
            service_socket = service_info.websocket
            request_id = invoke_request.invoke_id
            self.pending_requests[request_id] = asyncio.Future()
            e = invoke_request.encode()
            await self.send_message(service_socket, e)

            invoke_response = None
            async def _wait_for_invoke_response():
                nonlocal invoke_response
                invoke_response = await self.pending_requests[request_id]
                del self.pending_requests[request_id]
            await _wait_for_invoke_response()
            return invoke_response.encode()
        else:
            return {
                "status": "error",
                "message": f"Service '{invoke_request.service_id}' not found.",
            }

    async def handle_get_future_result(self, request: dict) -> dict:
        get_future_result_request = GetFutureResultRequest.decode(request)
        invoke_future = get_future_result_request.future
        if invoke_future.service_id in self.service_registry:
            service_info = self.service_registry[invoke_future.service_id]
            service_socket = service_info.websocket
            request_id = invoke_future.invoke_id
            self.pending_requests[request_id] = asyncio.Future()
            e = get_future_result_request.encode()
            await self.send_message(service_socket, e)

            invoke_response = await self.pending_requests[request_id]
            del self.pending_requests[request_id]
            return invoke_response.encode()
        else:
            return {
                "status": "error",
                "message": f"Service '{invoke_future.service_id}' not found.",
            }

    async def handle_worker_response(self, request: dict) -> None:
        invoke_response = InvokeServiceResponse.decode(request)
        invoke_id = invoke_response.invoke_id
        if invoke_id in self.pending_requests:
            self.pending_requests[invoke_id].set_result(invoke_response)

    async def handle_future_response(self, request: dict) -> None:
        future_response = FutureResponse.decode(request)
        invoke_id = future_response.future.invoke_id
        if invoke_id in self.pending_requests:
            self.pending_requests[invoke_id].set_result(future_response)

    def run(self, **kwargs) -> None:
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            **kwargs
        )


def run_server(host: str = "localhost", port: int = 8765, log_level: str = "WARNING", **kwargs) -> None:
    logger.remove()
    logger.add(sys.stdout, level=log_level)
    load_dotenv()
    server = MagiqueServer(host, port)
    _params = {}
    _params.update(kwargs)
    server.run(**_params)


if __name__ == "__main__":
    Fire(run_server)
