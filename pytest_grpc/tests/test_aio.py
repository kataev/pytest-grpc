import pytest
import grpc
import threading

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


# Asynchronous Stub and Asynchronous Server

@pytest.mark.asyncio
async def test_some(aio_grpc_stub, aio_grpc_server):
    request = EchoRequest()
    response = await aio_grpc_stub.handler(request)
    assert response.name == f'test-{request.name}'

@pytest.mark.asyncio
async def test_error(aio_grpc_stub, aio_grpc_server):
    request = EchoRequest()
    with pytest.raises(grpc.RpcError):
        response = await aio_grpc_stub.error_handler(request)
