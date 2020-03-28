import pytest
import threading

from stub.test_pb2 import EchoRequest, Empty


@pytest.fixture(scope='module')
def grpc_add_to_server():
    from stub.test_pb2_grpc import add_EchoServiceServicer_to_server

    return add_EchoServiceServicer_to_server


@pytest.fixture(scope='module')
def grpc_servicer():
    from servicer import Servicer

    return Servicer()


@pytest.fixture(scope='module')
def grpc_stub(grpc_channel):
    from stub.test_pb2_grpc import EchoServiceStub

    return EchoServiceStub(grpc_channel)


def test_some(grpc_stub):
    request = EchoRequest()
    response = grpc_stub.handler(request)

    assert response.name == f'test-{request.name}'

def test_example(grpc_stub):
    request = EchoRequest()
    response = grpc_stub.error_handler(request)

    assert response.name == f'test-{request.name}'


grpc_max_workers = 2


def test_blocking(grpc_stub):
    stream = grpc_stub.blocking(Empty())
    # after this call the servicer blocks its thread
    def call_unblock():
        # with grpc_max_workers = 1 this call could not be executed
        grpc_stub.unblock(Empty())
        grpc_stub.unblock(Empty())
    t = threading.Thread(target=call_unblock)
    t.start()
    for resp in stream:
        pass
    t.join()
