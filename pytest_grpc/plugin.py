import grpc
import pytest
import socket
from concurrent import futures


class FakeServer(object):
    def __init__(self):
        self.handlers = None

    def add_generic_rpc_handlers(self, generic_rpc_handlers):
        from grpc._server import _validate_generic_rpc_handlers
        _validate_generic_rpc_handlers(generic_rpc_handlers)

        self.handlers = generic_rpc_handlers[0]._method_handlers

    def start(self):
        pass

    def stop(self, grace=None):
        pass


class FakeContext(object):
    def abort(self, status_code, message):
        raise RuntimeError('Stop with %s - %s' % (status_code, message))


class FakeChannel:
    def __init__(self, fake_server):
        self.server = fake_server


for method_name in ['unary_unary', 'unary_stream', 'stream_unary', 'stream_stream']:
    def fake_method(name):
        def method(self, uri, *args, **kwargs):
            handler = self.server.handlers[uri]
            real_method = getattr(handler, name)

            def fake_handler(request):
                context = FakeContext()
                return real_method(request, context)

            return fake_handler

        method.__name__ = method_name
        setattr(FakeChannel, method_name, method)

        return method


    fake_method(method_name)

del fake_method, method_name


@pytest.fixture(scope='module')
def grpc_addr():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))

    return '{}:{}'.format(*sock.getsockname())


@pytest.fixture(scope='module')
def _grpc_server(request, grpc_addr, grpc_add_to_server, grpc_servicer):
    if request.config.getoption('grpc-fake'):
        server = FakeServer()
        grpc_add_to_server(grpc_servicer, server)
        yield server
    else:
        pool = futures.ThreadPoolExecutor(max_workers=1)

        server = grpc.server(pool)
        grpc_add_to_server(grpc_servicer, server)

        server.add_insecure_port(grpc_addr)
        yield server
        pool.shutdown(wait=False)


@pytest.fixture(scope='module')
def grpc_channel(request, _grpc_server, grpc_addr):
    if request.config.getoption('grpc-fake'):
        yield FakeChannel(_grpc_server)
    else:

        _grpc_server.start()
        with grpc.insecure_channel(grpc_addr) as channel:
            yield channel
        _grpc_server.stop(grace=None)


def pytest_addoption(parser):
    parser.addoption('--grpc-fake-server', action='store_true', dest='grpc-fake')
