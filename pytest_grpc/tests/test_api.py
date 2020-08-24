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


# Synchronous Stub and Synchronous Server

def test_some(grpc_stub, grpc_server):
    request = EchoRequest()
    response = grpc_stub.handler(request)
    assert response.name == f'test-{request.name}'


def test_error(grpc_stub, grpc_server):
    request = EchoRequest()
    with pytest.raises(grpc.RpcError):
        grpc_stub.error_handler(request)


def test_blocking(grpc_stub, grpc_server):
    stream = grpc_stub.blocking(Empty())
    def call_unblock():
        grpc_stub.unblock(Empty())
        grpc_stub.unblock(Empty())
    t = threading.Thread(target=call_unblock)
    t.start()
    for resp in stream:
        pass
    t.join()
