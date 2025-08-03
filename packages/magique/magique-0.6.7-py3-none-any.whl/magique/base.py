from .ser import Serializer


class NetworkObject:
    def __init__(self, serializer: Serializer):
        self.serializer = serializer

    async def send_message(self, websocket, message: dict):
        ser_message = self.serializer.serialize(message)
        await websocket.send(ser_message)

    async def receive_message(self, websocket) -> dict:
        message = await websocket.recv()
        return self.serializer.deserialize(message)
