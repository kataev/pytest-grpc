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
def grpc_add_to_servers():
    return [
        add_EchoServiceServicer_to_server,
        add_EchoServiceServicer_to_server,
    ]


@pytest.fixture
def grpc_servicers():
    return [
        Servicer,
        Servicer,
    ]


@pytest.fixture
def grpc_stub_classes():
    yield [
        EchoServiceStub,
        EchoServiceStub,
    ]


# Synchronous Stub and Synchronous Server

def test_multiple(grpc_stubs):
    svc1, svc2 = grpc_stubs
    request = EchoRequest()
    response1 = svc1.handler(request)
    response2 = svc2.handler(request)
    assert response1.name == f'test-{request.name}'
    assert response2.name == f'test-{request.name}'
