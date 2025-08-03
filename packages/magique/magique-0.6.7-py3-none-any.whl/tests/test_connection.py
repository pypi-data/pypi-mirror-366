import asyncio

import pytest
from executor.engine import Engine, ProcessJob

from magique.server import MagiqueServer
from magique.client import connect_to_server, MagiqueError
from magique.worker import MagiqueWorker


TEST_HOST = "localhost"
TEST_PORT = 9000
TEST_URL = f"ws://{TEST_HOST}:{TEST_PORT}/ws"


def start_server(port: int = TEST_PORT):
    server = MagiqueServer(TEST_HOST, port)
    server.run()


def start_worker():
    worker = MagiqueWorker("test_worker", TEST_URL)

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


async def test_basic_connection():
    engine = Engine()
    server_job = ProcessJob(start_server)
    await engine.submit_async(server_job)
    await asyncio.sleep(1)
    worker_job = ProcessJob(start_worker)
    await engine.submit_async(worker_job)
    await asyncio.sleep(5)

    server = await connect_to_server(TEST_URL)
    services = await server.list_services()
    assert len(services) == 1
    assert services[0].service_name == "test_worker"
    service = await server.get_service("test_worker")
    service_info = await service.fetch_service_info()
    assert service_info.service_name == "test_worker"
    #t1 = service.invoke("add_numbers", {"a": 1, "b": 2})
    #res = await t1
    #assert res == 3
    t2 = service.invoke("add_numbers", {"a": 2, "b": 2})
    t3 = service.invoke("add_numbers", {"a": 3, "b": 2})
    t4 = service.invoke("add_numbers", {"a": 4, "b": 2})
    res = await asyncio.gather(t4, t2, t3)
    assert res == [6, 4, 5]

    fut1 = await service.invoke(
        "add_numbers", {"a": 2, "b": 2}, return_future=True)
    fut2 = await service.invoke(
        "add_numbers", {"a": fut1, "b": 2}, return_future=True)
    res = await service.fetch_future_result(fut2)
    assert res == 6

    with pytest.raises(MagiqueError, match="test error"):
        try:
            await service.invoke("raise_error")
        except MagiqueError as e:
            print(e)
            raise

    with pytest.raises(MagiqueError, match="Function not found"):
        await service.invoke("not_exist")

    class TestClass:
        pass

    res = await service.invoke("print_obj", {"obj": TestClass()})
    assert res == "hello"

    size = 1 * int(1e6)  # 1 million, about 5MB
    res = await service.invoke("large_list", {"n": size})
    assert len(res) == size

    res = await service.invoke("get_client_id", {})
    assert res == service.server_proxy.client_id

    await service.close_connection()
    await worker_job.cancel()
    services = await server.list_services()
    assert len(services) == 0
    await server_job.cancel()


async def test_worker_with_multiple_servers():
    engine = Engine()
    server_jobs = []
    n_servers = 3
    for i in range(n_servers):
        server_jobs.append(ProcessJob(start_server, args=(TEST_PORT + i,)))
    await engine.submit_async(*server_jobs)
    await asyncio.sleep(1)

    not_existing_server = "ws://localhost:1111/ws"

    urls = [f"ws://{TEST_HOST}:{TEST_PORT + i}/ws" for i in range(n_servers)]
    urls = urls + [not_existing_server]

    def start_worker():
        worker = MagiqueWorker("test_worker", urls)

        @worker.register
        def add_numbers(a: int, b: int) -> int:
            return a + b

        asyncio.run(worker.run())

    worker_job = ProcessJob(start_worker)
    await engine.submit_async(worker_job)
    await asyncio.sleep(5)

    server = await connect_to_server(urls[0])
    services = await server.list_services()
    assert len(services) == 1
    assert services[0].service_name == "test_worker"
    server2 = await connect_to_server(urls[1])
    services = await server2.list_services()
    assert len(services) == 1
    assert services[0].service_name == "test_worker"

    service1 = await server.get_service("test_worker")
    await service1.fetch_service_info()
    service2 = await server2.get_service("test_worker")
    await service2.fetch_service_info()
    cor1 = service1.invoke("add_numbers", {"a": 1, "b": 2})
    cor2 = service2.invoke("add_numbers", {"a": 1, "b": 2})
    cor3 = service1.invoke("add_numbers", {"a": 1, "b": 10})
    cor4 = service2.invoke("add_numbers", {"a": 1, "b": 10})
    res = await asyncio.gather(cor1, cor2, cor3, cor4)
    assert res == [3, 3, 11, 11]
    await service1.close_connection()
    await service2.close_connection()

    service1 = await server.get_service("test_worker")
    service2 = await server2.get_service("test_worker")
    cor1 = service1.invoke("add_numbers", {"a": 1, "b": 2})
    cor2 = service2.invoke("add_numbers", {"a": 1, "b": 2})
    cor3 = service1.invoke("add_numbers", {"a": 1, "b": 10})
    cor4 = service2.invoke("add_numbers", {"a": 1, "b": 10})
    res = await asyncio.gather(cor1, cor2, cor3, cor4)
    assert res == [3, 3, 11, 11]
    await service1.close_connection()
    await service2.close_connection()

    await worker_job.cancel()
    services = await server.list_services()
    assert len(services) == 0
    services = await server2.list_services()
    assert len(services) == 0
    for job in server_jobs:
        await job.cancel()


async def test_multi_connection_server_proxy():
    engine = Engine()
    server_jobs = []
    n_servers = 3
    for i in range(n_servers):
        server_jobs.append(ProcessJob(start_server, args=(TEST_PORT + i,)))
    await engine.submit_async(*server_jobs)
    await asyncio.sleep(1)

    not_existing_server = "ws://localhost:1111/ws"
    urls = [f"ws://{TEST_HOST}:{TEST_PORT + i}/ws" for i in range(n_servers)]
    urls = urls + [not_existing_server]

    def start_worker():
        worker = MagiqueWorker("test_worker", urls)

        @worker.register
        def add_numbers(a: int, b: int) -> int:
            return a + b

        asyncio.run(worker.run())

    worker_job = ProcessJob(start_worker)
    await engine.submit_async(worker_job)
    await asyncio.sleep(5)

    server = await connect_to_server(urls)
    services = await server.list_services()
    assert len(services) == 1
    assert services[0].service_name == "test_worker"
    service = await server.get_service("test_worker")
    await service.fetch_service_info()
    res = await service.invoke("add_numbers", {"a": 1, "b": 2})
    assert res == 3
    c1 = service.invoke("add_numbers", {"a": 1, "b": 2})
    c2 = service.invoke("add_numbers", {"a": 1, "b": 3})
    c3 = service.invoke("add_numbers", {"a": 1, "b": 4})
    res = await asyncio.gather(c1, c2, c3)
    assert res == [3, 4, 5]
    await service.close_connection()

    await worker_job.cancel()
    services = await server.list_services()
    assert len(services) == 0
    for job in server_jobs:
        await job.cancel()


async def test_future_from_other_service():
    def start_worker1():
        worker = MagiqueWorker("worker1", TEST_URL)

        @worker.register
        def add_numbers(a: int, b: int) -> int:
            return a + b

        asyncio.run(worker.run())

    def start_worker2():
        worker = MagiqueWorker("worker2", TEST_URL)

        @worker.register
        def multiply_numbers(a: int, b: int) -> int:
            return a * b

        asyncio.run(worker.run())

    engine = Engine()
    server_job = ProcessJob(start_server)
    await engine.submit_async(server_job)
    await asyncio.sleep(2)
    worker1_job = ProcessJob(start_worker1)
    worker2_job = ProcessJob(start_worker2)
    await engine.submit_async(worker1_job, worker2_job)
    await asyncio.sleep(2)

    server = await connect_to_server(TEST_URL)
    service1 = await server.get_service("worker1")
    service2 = await server.get_service("worker2")
    fut1 = await service1.invoke(
        "add_numbers", {"a": 1, "b": 2}, return_future=True)
    fut2 = await service2.invoke(
        "multiply_numbers", {"a": fut1, "b": fut1}, return_future=True)
    res = await service2.fetch_future_result(fut2)
    assert res == 9

    await service1.close_connection()
    await service2.close_connection()
    await worker1_job.cancel()
    await worker2_job.cancel()
    await server_job.cancel()


async def test_reverse_callable():
    def start_worker():
        worker = MagiqueWorker("test_worker", TEST_URL)

        @worker.register
        async def call_reverse(func):
            return (await func()) + (await func())

        @worker.register
        async def get_1():
            return 1

        @worker.register
        async def call_reverse_long(func):
            res1 = await func()
            await asyncio.sleep(1)
            res2 = await func()
            return res1 + res2

        asyncio.run(worker.run())

    engine = Engine()
    server_job = ProcessJob(start_server)
    await engine.submit_async(server_job)
    await asyncio.sleep(1)

    worker_job = ProcessJob(start_worker)
    await engine.submit_async(worker_job)
    await asyncio.sleep(5)

    server = await connect_to_server(TEST_URL)
    service = await server.get_service("test_worker")

    task1 = asyncio.create_task(service.invoke("call_reverse_long", {"func": lambda: 1}))

    async def t2():
        await asyncio.sleep(0.5)
        return await service.invoke("get_1")
    task2 = asyncio.create_task(t2())
    await asyncio.gather(task1, task2)
    assert task1.result() == 2
    assert task2.result() == 1

    res = await service.invoke("call_reverse", {"func": lambda: 1})
    assert res == 2
    await service.close_connection()

    service = await server.get_service("test_worker")
    res = await service.invoke("call_reverse", {"func": lambda: 1})
    assert res == 2
    await service.close_connection()

    await worker_job.cancel()
    await server_job.cancel()


async def test_id_hash():
    worker1 = MagiqueWorker("test_worker", TEST_URL, id_hash="test")
    worker2 = MagiqueWorker("test_worker", TEST_URL, id_hash="test")
    assert worker1.service_id == worker2.service_id

    def start_worker1():
        asyncio.run(worker1.run())

    def start_worker2():
        asyncio.run(worker2.run())

    engine = Engine()
    server_job = ProcessJob(start_server)
    await engine.submit_async(server_job)
    await asyncio.sleep(1)
    worker1_job = ProcessJob(start_worker1)
    worker2_job = ProcessJob(start_worker2)
    await engine.submit_async(worker1_job)
    await asyncio.sleep(1)
    await engine.submit_async(worker2_job)
    await asyncio.sleep(1)
    await worker1_job.cancel()
    await worker2_job.cancel()
    await server_job.cancel()
