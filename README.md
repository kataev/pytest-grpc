# pytest-grpc

Write test for gRPC with pytest.


## Example

See example dir and/or read 'usage'.

## Usage

For example you have some proto file with rpc declaration.


```proto
syntax = "proto3";

package test.v1;


service EchoService {
    rpc handler(EchoRequest) returns (EchoResponse) {
    }
}


message EchoRequest {
    string name = 1;
}

message EchoResponse {
    string name = 1;
}

```

After compile it with grpcio-tools, you get *_pb2.py and *_pb2_grpc.py files, now you can write your service.

```python
from stub.test_pb2 import EchoRequest, EchoResponse
from stub.test_pb2_grpc import EchoServiceServicer


class Servicer(EchoServiceServicer):
    def handler(self, request: EchoRequest, context) -> EchoResponse:
        return EchoResponse(name=f'test-{request.name}')

    def error_handler(self, request: EchoRequest, context) -> EchoResponse:
        raise RuntimeError('Some error')
```

Point pytest with your stubs and service:

```python
import pytest

from stub.test_pb2 import EchoRequest


@pytest.fixture(scope='module')
def grpc_add_to_server():
    from stub.test_pb2_grpc import add_EchoServiceServicer_to_server

    return add_EchoServiceServicer_to_server


@pytest.fixture(scope='module')
def grpc_servicer():
    from servicer import Servicer

    return Servicer()


@pytest.fixture(scope='module')
def grpc_stub_cls(grpc_channel):
    from stub.test_pb2_grpc import EchoServiceStub

    return EchoServiceStub
```

Write little test:
```python

def test_some(grpc_stub):
    request = EchoRequest()
    response = grpc_stub.handler(request)

    assert response.name == f'test-{request.name}'

def test_example(grpc_stub):
    request = EchoRequest()
    response = grpc_stub.error_handler(request)

    assert response.name == f'test-{request.name}'
``` 

#### Testing secure server

```python
from pathlib import Path
import pytest
import grpc

@pytest.fixture(scope='module')
def grpc_add_to_server():
    from stub.test_pb2_grpc import add_EchoServiceServicer_to_server

    return add_EchoServiceServicer_to_server


@pytest.fixture(scope='module')
def grpc_servicer():
    from servicer import Servicer

    return Servicer()


@pytest.fixture(scope='module')
def grpc_stub_cls(grpc_channel):
    from stub.test_pb2_grpc import EchoServiceStub

    return EchoServiceStub


@pytest.fixture(scope='session')
def my_ssl_key_path():
    return Path('/path/to/key.pem')


@pytest.fixture(scope='session')
def my_ssl_cert_path():
    return Path('/path/to/cert.pem')


@pytest.fixture(scope='module')
def grpc_server(_grpc_server, grpc_addr, my_ssl_key_path, my_ssl_cert_path):
    """
    Overwrites default `grpc_server` fixture with ssl credentials
    """
    credentials = grpc.ssl_server_credentials([
        (my_ssl_key_path.read_bytes(),
         my_ssl_cert_path.read_bytes())
    ])

    _grpc_server.add_secure_port(grpc_addr, server_credentials=credentials)
    _grpc_server.start()
    yield _grpc_server
    _grpc_server.stop(grace=None)


@pytest.fixture(scope='module')
def my_channel_ssl_credentials(my_ssl_cert_path):
    # If we're using self-signed certificate it's necessarily to pass root certificate to channel
    return grpc.ssl_channel_credentials(
        root_certificates=my_ssl_cert_path.read_bytes()
    )


@pytest.fixture(scope='module')
def grpc_channel(my_channel_ssl_credentials, create_channel):
    """
    Overwrites default `grpc_channel` fixture with ssl credentials
    """
    with create_channel(my_channel_ssl_credentials) as channel:
        yield channel

        
@pytest.fixture(scope='module')
def grpc_authorized_channel(my_channel_ssl_credentials, create_channel):
    """
    Channel with authorization header passed
    """
    grpc_channel_credentials = grpc.access_token_call_credentials("some_token")
    composite_credentials = grpc.composite_channel_credentials(
        my_channel_ssl_credentials,
        grpc_channel_credentials
    )
    with create_channel(composite_credentials) as channel:
        yield channel
    
    
@pytest.fixture(scope='module')
def my_authorized_stub(grpc_stub_cls, grpc_channel):
    """
    Stub with authorized channel
    """
    return grpc_stub_cls(grpc_channel)

```

## Run tests against real gRPC server
Run tests against read grpc server worked in another thread:

```bash
py.test
```

```
cachedir: .pytest_cache
plugins: grpc-0.0.0
collected 2 items

example/test_example.py::test_some PASSED
example/test_example.py::test_example FAILED

=================================== FAILURES ====================================
_________________________________ test_example __________________________________

grpc_stub = <stub.test_pb2_grpc.EchoServiceStub object at 0x107a9b390>

    def test_example(grpc_stub):
        request = EchoRequest()
>       response = grpc_stub.error_handler(request)

example/test_example.py:35:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
.env/lib/python3.7/site-packages/grpc/_channel.py:547: in __call__
    return _end_unary_response_blocking(state, call, False, None)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

state = <grpc._channel._RPCState object at 0x107b263c8>
call = <grpc._cython.cygrpc.SegregatedCall object at 0x107b323c8>
with_call = False, deadline = None

    def _end_unary_response_blocking(state, call, with_call, deadline):
        if state.code is grpc.StatusCode.OK:
            if with_call:
                rendezvous = _Rendezvous(state, call, None, deadline)
                return state.response, rendezvous
            else:
                return state.response
        else:
>           raise _Rendezvous(state, None, None, deadline)
E           grpc._channel._Rendezvous: <_Rendezvous of RPC that terminated with:
E           	status = StatusCode.UNKNOWN
E           	details = "Exception calling application: Some error"
E           	debug_error_string = "{"created":"@1544451353.148337000","description":"Error received from peer","file":"src/core/lib/surface/call.cc","file_line":1036,"grpc_message":"Exception calling application: Some error","grpc_status":2}"
E           >

.env/lib/python3.7/site-packages/grpc/_channel.py:466: _Rendezvous
------------------------------- Captured log call -------------------------------
_server.py                 397 ERROR    Exception calling application: Some error
Traceback (most recent call last):
  File "pytest-grpc/.env/lib/python3.7/site-packages/grpc/_server.py", line 389, in _call_behavior
    return behavior(argument, context), True
  File "pytest-grpc/example/src/servicer.py", line 10, in error_handler
    raise RuntimeError('Some error')
RuntimeError: Some error
================ 1 failed, 1 passed, 1 warnings in 0.16 seconds =================

```

## Run tests directly to python code
Call handlers directly, with fake grpc internals:

```bash
py.test --grpc-fake-server
```

In this case your get nice direct exceptions:

```
============================= test session starts =============================
cachedir: .pytest_cache
plugins: grpc-0.0.0
collected 2 items

example/test_example.py::test_some PASSED
example/test_example.py::test_example FAILED

================================== FAILURES ===================================
________________________________ test_example _________________________________

grpc_stub = <stub.test_pb2_grpc.EchoServiceStub object at 0x10e06f518>

    def test_example(grpc_stub):
        request = EchoRequest()
>       response = grpc_stub.error_handler(request)

example/test_example.py:35:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
pytest_grpc/plugin.py:42: in fake_handler
    return real_method(request, context)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <servicer.Servicer object at 0x10ce75278>, request =
context = <pytest_grpc.plugin.FakeContext object at 0x10e083e48>

    def error_handler(self, request: EchoRequest, context) -> EchoResponse:
>       raise RuntimeError('Some error')
E       RuntimeError: Some error

example/src/servicer.py:10: RuntimeError
=============== 1 failed, 1 passed, 1 warnings in 0.10 seconds ================
```

## Run the servicer on multiple threads
The number of workers threads for gRPC can be specified in two ways:

  - add `--grpc-max-workers=<n>` to the arguments
  - test modules can also use a `grpc_max_workers=<n>` variable

See `test_blocking` in example.
