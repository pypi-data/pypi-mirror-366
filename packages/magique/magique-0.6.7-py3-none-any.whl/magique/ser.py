import abc

import msgpack
import cloudpickle


class Serializer(abc.ABC):
    @abc.abstractmethod
    def serialize(self, data: dict) -> bytes:
        pass

    @abc.abstractmethod
    def deserialize(self, data: bytes) -> dict:
        pass


class DefaultSerializer(Serializer):
    def serialize_pyobj(self, data: object) -> bytes:
        return cloudpickle.dumps(data)

    def deserialize_pyobj(self, data: bytes) -> object:
        return cloudpickle.loads(data)

    def mixed_serialize(self, data: dict) -> bytes:
        """Try to serialize the data as msgpack, if that fails, serialize as pyobj"""
        try:
            method = "msgpack"
            payload = msgpack.packb(data)
        except:
            method = "cloudpickle"
            payload = self.serialize_pyobj(data)
        return msgpack.packb({"method": method, "payload": payload})

    def mixed_deserialize(self, data: bytes) -> object:
        """Try to deserialize the data as msgpack, if that fails, deserialize as pyobj"""
        data_decoded = msgpack.unpackb(data)
        method = data_decoded["method"]
        payload = data_decoded["payload"]
        if method == "msgpack":
            return msgpack.unpackb(payload)
        elif method == "cloudpickle":
            return self.deserialize_pyobj(payload)
        else:
            raise ValueError(f"Unknown method: {method}")

    def serialize(self, data: dict, pack_inner: bool = True) -> bytes:
        action = data.get("action")
        if pack_inner:
            if action in ("invoke_service", "reverse_invoke"):
                parameters = data["parameters"]
                ser_parameters = {}
                for key, value in parameters.items():
                    ser_parameters[key] = self.mixed_serialize(value)
                return msgpack.packb({**data, "parameters": ser_parameters})
            elif action in ("worker_response", "reverse_invoke_result"):
                result = data.pop("result")
                ser_result = self.mixed_serialize(result)
                return msgpack.packb({**data, "result": ser_result})
        return msgpack.packb(data)

    def deserialize(self, data: bytes, unpack_inner: bool = True) -> dict:
        res: dict = msgpack.unpackb(data)
        if not ("action" in res):
            return res
        action = res["action"]

        if unpack_inner:
            if action in ("invoke_service", "reverse_invoke"):
                ser_parameters = res.pop("parameters")
                parameters = {}
                for key, value in ser_parameters.items():
                    parameters[key] = self.mixed_deserialize(value)
                res["parameters"] = parameters
            elif action in ("worker_response", "reverse_invoke_result"):
                result = res.pop("result")
                if isinstance(result, bytes):
                    ser_result = self.mixed_deserialize(result)
                else:
                    ser_result = result
                res["result"] = ser_result
        return res
