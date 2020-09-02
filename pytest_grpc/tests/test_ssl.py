import pytest
import py
import os
import grpc
import asyncio
import packaging.version
import threading
import pytest_grpc

from .example_pb2 import EchoRequest, Empty
from .servicer import Servicer
from .example_pb2_grpc import add_EchoServiceServicer_to_server, EchoServiceStub


aio_available = pytest.mark.skipif(
    packaging.version.parse(grpc.__version__) < packaging.version.parse("1.31.0"),
    reason="aio test only work with grpcio versions 1.31.0 and later"
)


# Data loading fixtures

@pytest.fixture
def datadir(request):
    """ Search test assets in test-specific directory. """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    return py.path.local(test_dir)


@pytest.fixture
def key(datadir):
    """ SSL private key """
    with open(datadir.join('key.pem'), 'rb') as f:
        return f.read()


@pytest.fixture
def cert(datadir):
    """ Self-signed SSL root cert """
    with open(datadir.join('cert.pem'), 'rb') as f:
        return f.read()


@pytest.fixture
def grpc_add_to_server():
    return add_EchoServiceServicer_to_server


@pytest.fixture
def grpc_servicer():
    return Servicer


@pytest.fixture
def grpc_stub_cls():
    yield EchoServiceStub


# SSL Credentials for Server and Client

@pytest.fixture
def grpc_server_credentials(key, cert):
    return grpc.ssl_server_credentials([
        (key, cert),
    ])


@pytest.fixture
def grpc_channel_credentials(cert):
    return grpc.ssl_channel_credentials(cert)


def test_ssl(grpc_stub):
    request = EchoRequest()
    response = grpc_stub.handler(request)
    assert response.name == f'test-{request.name}'


@aio_available
@pytest.mark.asyncio
async def test_ssl_async(aio_grpc_stub):
    request = EchoRequest()
    response = await aio_grpc_stub.handler(request)
    assert response.name == f'test-{request.name}'
