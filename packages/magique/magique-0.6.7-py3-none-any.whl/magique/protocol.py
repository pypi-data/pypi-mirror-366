import typing as T
import json
import uuid

from funcdesc import Description

from .utils.log import logger


class Protocol:
    pass


class ServiceInfo(Protocol):
    def __init__(
        self,
        service_id: str,
        service_name: str,
        description: str,
        functions_description: T.Dict[str, Description],
        need_auth: bool = False,
        visible: bool = True,
    ):
        self.service_id = service_id
        self.service_name = service_name
        self.description = description
        self.functions_description = functions_description
        self.need_auth = need_auth
        self.visible = visible

    @classmethod
    def decode(cls, encoded: dict) -> "ServiceInfo":
        try:
            functions_description = {
                name: Description.from_json(json.dumps(desc))
                for name, desc in encoded["functions_description"].items()
            }
            info = cls(
                service_id=encoded["service_id"],
                service_name=encoded["service_name"],
                description=encoded["description"],
                functions_description=functions_description,
                need_auth=encoded["need_auth"],
                visible=encoded.get("visible", True),
            )
        except Exception as e:
            logger.error(f"Error creating ServiceInfo:\n{e}")
            raise
        return info

    def encode(self) -> dict:
        descs = {}
        for name, desc in self.functions_description.items():
            json_dict = json.loads(desc.to_json())
            descs[name] = json_dict
        return {
            "service_id": self.service_id,
            "service_name": self.service_name,
            "description": self.description,
            "functions_description": descs,
            "need_auth": self.need_auth,
            "visible": self.visible,
        }

    def __repr__(self):
        return f"ServiceInfo(service_id={self.service_id}, service_name={self.service_name})"


class RegisterServiceRequest(Protocol):
    def __init__(self, service_info: ServiceInfo):
        self.service_info = service_info

    def encode(self) -> dict:
        return {
            "action": "register_service",
            **self.service_info.encode(),
        }

    @classmethod
    def decode(cls, request: dict) -> "RegisterServiceRequest":
        service_info = ServiceInfo.decode(request)
        return cls(service_info)


class ClientInfo(Protocol):
    def __init__(self, client_id: str):
        self.client_id = client_id
    
    def encode(self) -> dict:
        return {
            "client_id": self.client_id,
        }

    @classmethod
    def decode(cls, request: dict) -> "ClientInfo":
        return cls(client_id=request["client_id"])


class RegisterClientRequest(Protocol):
    def __init__(self, client_id: str):
        self.client_info = ClientInfo(client_id)
    
    def encode(self) -> dict:
        return {
            "action": "register_client",
            **self.client_info.encode(),
        }

    @classmethod
    def decode(cls, request: dict) -> "RegisterClientRequest":
        return cls(client_id=request["client_id"])


class InvokeServiceRequest(Protocol):
    def __init__(
        self,
        client_id: str,
        service_id: str,
        function_name: str,
        parameters: dict,
        invoke_id: T.Optional[str] = None,
        return_future: bool = False,
    ):
        self.client_id = client_id
        self.service_id = service_id
        self.function_name = function_name
        self.parameters = parameters
        self.invoke_id = invoke_id or str(uuid.uuid4())
        self.return_future = return_future

    def encode(self) -> dict:
        return {
            "action": "invoke_service",
            "client_id": self.client_id,
            "invoke_id": self.invoke_id,
            "service_id": self.service_id,
            "function_name": self.function_name,
            "parameters": self.parameters,
            "return_future": self.return_future,
        }

    @classmethod
    def decode(cls, request: dict) -> "InvokeServiceRequest":
        return cls(
            client_id=request["client_id"],
            service_id=request["service_id"],
            function_name=request["function_name"],
            parameters=request["parameters"],
            invoke_id=request.get("invoke_id"),
            return_future=request.get("return_future", False),
        )


class InvokeServiceResponse(Protocol):
    def __init__(self, invoke_id: str, status: str, result: dict):
        self.invoke_id = invoke_id
        self.status = status
        self.result = result

    def encode(self) -> dict:
        return {
            "action": "worker_response",
            "invoke_id": self.invoke_id,
            "status": self.status,
            "result": self.result,
        }

    @classmethod
    def decode(cls, response: dict) -> "InvokeServiceResponse":
        return cls(
            invoke_id=response["invoke_id"],
            status=response["status"],
            result=response["result"],
        )


class InvokeFuture(Protocol):
    def __init__(
        self,
        invoke_id: str,
        service_id: str,
    ):
        self.invoke_id = invoke_id
        self.service_id = service_id

    def encode(self) -> dict:
        return {
            "invoke_id": self.invoke_id,
            "service_id": self.service_id,
        }

    @classmethod
    def decode(cls, request: dict) -> "InvokeFuture":
        return cls(
            invoke_id=request["invoke_id"],
            service_id=request["service_id"],
        )


class FutureResponse(Protocol):
    def __init__(self, future: InvokeFuture):
        self.future = future

    def encode(self) -> dict:
        return {
            "action": "future_response",
            **self.future.encode(),
        }

    @classmethod
    def decode(cls, request: dict) -> "FutureResponse":
        return cls(
            future=InvokeFuture.decode(request),
        )


class GetFutureResultRequest(Protocol):
    def __init__(self, future: InvokeFuture):
        self.future = future

    def encode(self) -> dict:
        return {
            "action": "get_future_result",
            **self.future.encode(),
        }

    @classmethod
    def decode(cls, request: dict) -> "GetFutureResultRequest":
        return cls(
            future=InvokeFuture.decode(request),
        )
