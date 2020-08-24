import grpc
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
