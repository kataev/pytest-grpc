import socket
from concurrent import futures

import grpc
from grpc.experimental import aio
import pytest
import inspect
import asyncio


def assert_async(request):
    if not is_async_node(request):
        pytest.fail(
            'You are trying to use an asynchronous aio_ fixture with a synchronous test function. ' \
            'Either remove the aio_ prefix or make the function a coroutine. ' \
            'Requested fixtures: {}'.format(", ".join(request.fixturenames))
        )


def assert_sync(request):
    if is_async_node(request):
        pytest.fail(
            'You are trying to use a synchronous fixture with a asynchronous test coroutine. ' \
            'Either add the aio_ prefix or make the coroutine a function. ' \
            'Requested fixtures: {}'.format(", ".join(request.fixturenames))
    )


def is_async_node(request):
    return (
        inspect.iscoroutinefunction(request.function) or
        bool(request.node.get_closest_marker('asyncio'))
    )


# General Server fixtures

@pytest.fixture
def grpc_addr(unused_tcp_port):
    yield f'localhost:{unused_tcp_port}'


@pytest.fixture
def grpc_interceptors():
    return None


@pytest.fixture
def grpc_channel_credentials():
    return grpc.local_channel_credentials()


@pytest.fixture
def grpc_server_credentials():
    return grpc.local_server_credentials()



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
def grpc_server(request, thread_pool, grpc_addr, grpc_add_to_server, grpc_servicer, grpc_interceptors, grpc_server_credentials):
    assert_sync(request)

    server = grpc.server(thread_pool, interceptors=grpc_interceptors)
    grpc_add_to_server(grpc_servicer(), server)
    server.add_secure_port(grpc_addr, grpc_server_credentials)
    server.start()
    yield server
    server.stop(grace=None)


# Synchronous Client fixtures

@pytest.fixture
def grpc_create_channel(request, grpc_addr, grpc_channel_credentials):
    return grpc.secure_channel(grpc_addr, grpc_channel_credentials)


@pytest.fixture
def grpc_channel(request, grpc_create_channel):
    with grpc_create_channel as channel:
        yield channel


@pytest.fixture
def grpc_stub(request, grpc_stub_cls, grpc_channel, grpc_server):
    return grpc_stub_cls(grpc_channel)


# Asynchronous Server fixtures

@pytest.fixture
def aio_grpc_server(request, event_loop, grpc_addr, grpc_add_to_server, grpc_servicer, grpc_interceptors, grpc_server_credentials):
    assert_async(request)

    async def run(server):
        await server.start()

    async def stop(server):
        await server.stop(grace=None)

    server = aio.server(interceptors=grpc_interceptors)
    grpc_add_to_server(grpc_servicer(), server)
    server.add_secure_port(grpc_addr, grpc_server_credentials)
    event_loop.run_until_complete(run(server))
    yield server
    event_loop.run_until_complete(stop(server))


# Asynchronous Client fixtures

@pytest.fixture
def aio_grpc_create_channel(request, grpc_addr, grpc_channel_credentials):
    return aio.secure_channel(grpc_addr, grpc_channel_credentials)


@pytest.mark.asyncio
@pytest.fixture
async def aio_grpc_channel(request, aio_grpc_create_channel):
    async with aio_grpc_create_channel as channel:
        yield channel


@pytest.fixture
def aio_grpc_stub(request, grpc_stub_cls, aio_grpc_channel, aio_grpc_server):
    return grpc_stub_cls(aio_grpc_channel)


def pytest_addoption(parser):
    parser.addoption('--grpc-max-workers', type=int, dest='grpc-max-workers', default=2)
