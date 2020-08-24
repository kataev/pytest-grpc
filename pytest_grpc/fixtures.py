import socket
from concurrent import futures

import grpc
import pytest


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
def grpc_server(thread_pool, grpc_addr, grpc_add_to_server, grpc_servicer, grpc_interceptors):
    server = grpc.server(thread_pool, interceptors=grpc_interceptors)
    grpc_add_to_server(grpc_servicer(), server)
    server.add_insecure_port(grpc_addr)
    server.start()
    yield server
    server.stop(grace=None)


# Synchronous Client fixtures

@pytest.fixture
def grpc_create_channel(request, grpc_addr):
    return grpc.insecure_channel(grpc_addr)


@pytest.fixture
def grpc_channel(grpc_create_channel):
    with grpc_create_channel as channel:
        yield channel


@pytest.fixture
def grpc_stub(grpc_stub_cls, grpc_channel):
    return grpc_stub_cls(grpc_channel)
