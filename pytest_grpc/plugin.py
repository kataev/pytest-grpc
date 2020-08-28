import socket
from concurrent import futures

import grpc
from grpc.experimental import aio
import pytest
import inspect
import asyncio


class UseAsyncError(pytest.UsageError):
    def __init__(self, msg='You are trying to use an asynchronous aio_ fixture with a synchronous test function. Either remove the aio_ prefix or make the function a coroutine.', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class UseSyncError(pytest.UsageError):
    def __init__(self, msg='You are trying to use a synchronous fixture with a asynchronous test coroutine. Either add the aio_ prefix or make the coroutine a function.', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


def is_async_node(request):
    return (
        inspect.iscoroutinefunction(request.function) or
        bool(request.node.get_closest_marker('asyncio'))
    )


# General Server fixtures

@pytest.fixture
def grpc_addr():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    ip, port = sock.getsockname()
    yield f'localhost:{port}'
    sock.close()


@pytest.fixture
def grpc_interceptors():
    return None


# Synchronous Server fixtures

@pytest.fixture(scope="session")
def grpc_max_workers(request):
    return request.config.getoption('grpc-max-workers')


@pytest.fixture(scope="session")
def thread_pool(request, grpc_max_workers):
    pool = futures.ThreadPoolExecutor(max_workers=grpc_max_workers)
    yield pool
    pool.shutdown(wait=False)


@pytest.fixture
def grpc_server(request, thread_pool, grpc_addr, grpc_add_to_server, grpc_servicer, grpc_interceptors):
    if is_async_node(request):
        raise UseSyncError()

    server = grpc.server(thread_pool, interceptors=grpc_interceptors)
    grpc_add_to_server(grpc_servicer(), server)
    server.add_insecure_port(grpc_addr)
    server.start()
    yield server
    server.stop(grace=None)


# Synchronous Client fixtures

@pytest.fixture
def grpc_create_channel(request, grpc_addr):
    if is_async_node(request):
        raise UseSyncError()

    return grpc.insecure_channel(grpc_addr)


@pytest.fixture
def grpc_channel(request, grpc_create_channel):
    if is_async_node(request):
        raise UseSyncError()

    with grpc_create_channel as channel:
        yield channel


@pytest.fixture
def grpc_stub(request, grpc_stub_cls, grpc_channel):
    if is_async_node(request):
        raise UseSyncError()

    return grpc_stub_cls(grpc_channel)


# Asynchronous Server fixtures

@pytest.fixture
def aio_grpc_server(request, event_loop, grpc_addr, grpc_add_to_server, grpc_servicer, grpc_interceptors):
    if not is_async_node(request):
        raise UseAsyncError()

    async def run(server):
        await server.start()

    async def stop(server):
        await server.stop(grace=None)

    server = aio.server(interceptors=grpc_interceptors)
    grpc_add_to_server(grpc_servicer(), server)
    server.add_insecure_port(grpc_addr)
    event_loop.run_until_complete(run(server))
    yield server
    event_loop.run_until_complete(stop(server))


# Asynchronous Client fixtures

@pytest.fixture
def aio_grpc_create_channel(request, grpc_addr):
    if not is_async_node(request):
        raise UseAsyncError()

    return aio.insecure_channel(grpc_addr)


@pytest.mark.asyncio
@pytest.fixture
async def aio_grpc_channel(request, event_loop, aio_grpc_create_channel):
    if not is_async_node(request):
        raise UseAsyncError()

    async with aio_grpc_create_channel as channel:
        yield channel


@pytest.fixture
def aio_grpc_stub(request, grpc_stub_cls, aio_grpc_channel):
    if not is_async_node(request):
        raise UseAsyncError()
    
    return grpc_stub_cls(aio_grpc_channel)


def pytest_addoption(parser):
    parser.addoption('--grpc-fake-server', action='store_true', dest='grpc-fake')
    parser.addoption('--grpc-max-workers', type=int, dest='grpc-max-workers', default=2)
