import pytest
from pytest_grpc import aio_available
import grpc
import asyncio
import threading
import pytest_grpc

from .example_pb2 import EchoRequest, Empty
from .servicer import Servicer
from .example_pb2_grpc import add_EchoServiceServicer_to_server, EchoServiceStub


@pytest.fixture
def grpc_add_to_server():
    return add_EchoServiceServicer_to_server


@pytest.fixture
def grpc_servicer():
    return Servicer


@pytest.fixture
def grpc_stub_cls():
    yield EchoServiceStub


# Synchronous Stub and Synchronous Server

def test_some(grpc_stub):
    request = EchoRequest()
    response = grpc_stub.handler(request)
    assert response.name == f'test-{request.name}'


def test_error(grpc_stub):
    request = EchoRequest()
    with pytest.raises(grpc.RpcError) as e:
        grpc_stub.error_handler(request)

    assert e.value.code() == grpc.StatusCode.UNKNOWN


def test_blocking(grpc_stub):
    stream = grpc_stub.blocking(Empty())
    def call_unblock():
        grpc_stub.unblock(Empty())
        grpc_stub.unblock(Empty())
    t = threading.Thread(target=call_unblock)
    t.start()
    for resp in stream:
        pass
    t.join()


# Asynchronous Stub and Asynchronous Server

@aio_available
@pytest.mark.asyncio
async def test_some_async(aio_grpc_stub):
    request = EchoRequest()
    response = await aio_grpc_stub.handler(request)
    assert response.name == f'test-{request.name}'

@aio_available
@pytest.mark.asyncio
async def test_error_async(aio_grpc_stub):
    request = EchoRequest()
    with pytest.raises(grpc.RpcError) as e:
        response = await aio_grpc_stub.error_handler(request)

    assert e.value.code() == grpc.StatusCode.UNKNOWN

@aio_available
@pytest.mark.asyncio
async def test_blocking_async(aio_grpc_stub):
    async def call_unblock():
        await aio_grpc_stub.unblock(Empty())
        await aio_grpc_stub.unblock(Empty())

    async def call_block():
        async for resp in aio_grpc_stub.blocking(Empty()):
            pass

    await asyncio.gather(
        call_block(),
        call_unblock(),
    )


# Incorrect fixtures requested

@pytest.mark.xfail(strict=True)
@pytest.mark.asyncio
async def test_sync_fixture_async_test(grpc_stub):
    pass


@pytest.mark.xfail(strict=True)
def test_async_fixture_sync_test(aio_grpc_stub):
    pass
