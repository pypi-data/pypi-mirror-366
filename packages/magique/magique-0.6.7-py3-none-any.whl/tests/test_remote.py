import asyncio

from executor.engine import Engine, ProcessJob

from magique.worker import MagiqueWorker
from magique.client import connect_to_server

server_urls = [
    "ws://server.magique1.aristoteleo.com/ws",
    "ws://server.magique2.aristoteleo.com/ws",
    "ws://magique.heartst.aristoteleo.com/ws",
    "ws://magique.spateo.aristoteleo.com/ws",
    "ws://magique3.aristoteleo.com/ws",
]


def start_worker():
    worker = MagiqueWorker("test_worker", server_urls)

    @worker.register(job_type="process")
    def add_numbers(a: int, b: int) -> int:
        return a + b

    @worker.register
    def print_obj(obj: object) -> str:
        print(obj)
        return 'hello'

    @worker.register
    def large_list(n: int) -> list:
        return list(range(n))

    @worker.register
    def raise_error():
        raise Exception("test error")

    @worker.register
    def get_client_id(__client_id__: str) -> str:
        return __client_id__

    async def after_register(_):
        print("after register")

    asyncio.run(worker.run(after_register=after_register))


async def test_remote_servers():
    executor = Engine()
    worker_job = ProcessJob(start_worker)
    await executor.submit_async(worker_job)
    await asyncio.sleep(1)
    server_proxy = await connect_to_server(server_urls)
    service = await server_proxy.get_service("test_worker")
    await service.fetch_service_info()
    res = await service.invoke("add_numbers", {"a": 1, "b": 2})
    assert res == 3
    cor1 = service.invoke("add_numbers", {"a": 1, "b": 2})
    cor2 = service.invoke("add_numbers", {"a": 1, "b": 3})
    cor3 = service.invoke("add_numbers", {"a": 1, "b": 4})
    res = await asyncio.gather(cor1, cor2, cor3)
    assert res == [3, 4, 5]
    await worker_job.cancel()


if __name__ == "__main__":
    asyncio.run(test_remote_servers())