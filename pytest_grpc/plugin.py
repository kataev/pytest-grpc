import socket
from concurrent import futures

import grpc
import pytest
from grpc._cython.cygrpc import CompositeChannelCredentials, _Metadatum


class FakeServer(object):
    def __init__(self, pool):
        self.handlers = {}
        self.pool = pool

    def add_generic_rpc_handlers(self, generic_rpc_handlers):
        from grpc._server import _validate_generic_rpc_handlers
        _validate_generic_rpc_handlers(generic_rpc_handlers)

        self.handlers.update(generic_rpc_handlers[0]._method_handlers)

    def start(self):
        pass

    def stop(self, grace=None):
        pass

    def add_secure_port(self, target, server_credentials):
        pass

    def add_insecure_port(self, target):
        pass


class FakeRpcError(RuntimeError, grpc.RpcError):
    def __init__(self, code, details):
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details


class FakeContext(object):
    def __init__(self):
        self._invocation_metadata = []

    def abort(self, code, details):
        raise FakeRpcError(code, details)

    def invocation_metadata(self):
        return self._invocation_metadata


class FakeChannel:
    def __init__(self, fake_server, credentials):
        self.server = fake_server
        self._credentials = credentials

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def fake_method(self, method_name, uri, *args, **kwargs):
        handler = self.server.handlers[uri]
        real_method = getattr(handler, method_name)

        def fake_handler(request):
            context = FakeContext()

            def metadata_callbak(metadata, error):
                context._invocation_metadata.extend((_Metadatum(k, v) for k, v in metadata))

            if self._credentials and isinstance(self._credentials._credentials, CompositeChannelCredentials):
                for call_cred in self._credentials._credentials._call_credentialses:
                    call_cred._metadata_plugin._metadata_plugin(context, metadata_callbak)
            future = self.server.pool.submit(real_method, request, context)
            return future.result()

        return fake_handler

    def unary_unary(self, *args, **kwargs):
        return self.fake_method('unary_unary', *args, **kwargs)

    def unary_stream(self, *args, **kwargs):
        return self.fake_method('unary_stream', *args, **kwargs)

    def stream_unary(self, *args, **kwargs):
        return self.fake_method('stream_unary', *args, **kwargs)

    def stream_stream(self, *args, **kwargs):
        return self.fake_method('stream_stream', *args, **kwargs)


@pytest.fixture(scope='module')
def grpc_addr():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    return 'localhost:{}'.format(sock.getsockname()[1])


@pytest.fixture(scope='module')
def grpc_interceptors():
    return


@pytest.fixture(scope='module')
def _grpc_server(request, grpc_addr, grpc_interceptors):
    max_workers = request.config.getoption('grpc-max-workers')
    try:
        max_workers = max(request.module.grpc_max_workers, max_workers)
    except AttributeError:
        pass
    pool = futures.ThreadPoolExecutor(max_workers=max_workers)
    if request.config.getoption('grpc-fake'):
        server = FakeServer(pool)
        yield server
    else:
        server = grpc.server(pool, interceptors=grpc_interceptors)
        yield server
    pool.shutdown(wait=False)


@pytest.fixture(scope='module')
def grpc_server(_grpc_server, grpc_addr, grpc_add_to_server, grpc_servicer):
    grpc_add_to_server(grpc_servicer, _grpc_server)
    _grpc_server.add_insecure_port(grpc_addr)
    _grpc_server.start()
    yield _grpc_server
    _grpc_server.stop(grace=None)


@pytest.fixture(scope='module')
def grpc_create_channel(request, grpc_addr, grpc_server):
    def _create_channel(credentials=None, options=None):
        if request.config.getoption('grpc-fake'):
            return FakeChannel(grpc_server, credentials)
        if credentials is not None:
            return grpc.secure_channel(grpc_addr, credentials, options)
        return grpc.insecure_channel(grpc_addr, options)

    return _create_channel


@pytest.fixture(scope='module')
def grpc_channel(grpc_create_channel):
    with grpc_create_channel() as channel:
        yield channel


@pytest.fixture(scope='module')
def grpc_stub(grpc_stub_cls, grpc_channel):
    return grpc_stub_cls(grpc_channel)


def pytest_addoption(parser):
    parser.addoption('--grpc-fake-server', action='store_true', dest='grpc-fake')
    parser.addoption('--grpc-max-workers', type=int, dest='grpc-max-workers', default=1)
