# pytest-grpc

Write test for gRPC with pytest.

## Usage

### Simple

Define your gRPC servicer in the fixtures `grpc_add_to_server`, `grpc_servicer`, and `grpc_stub_cls` and run your tests requesting the `grpc_stub` fixture

```python
import pytest
from test_pb2 import EchoRequest
from test_pb2_grpc import add_EchoServiceServicer_to_server, EchoServiceStub
from servicer import Servicer

@pytest.fixture
def grpc_add_to_server():
    return add_EchoServiceServicer_to_server


@pytest.fixture
def grpc_servicer():
    return Servicer


@pytest.fixture
def grpc_stub_cls():
    return EchoServiceStub


def test_some(grpc_stub):
    request = EchoRequest()
    response = grpc_stub.handler(request)
    assert response.name == f'test-{request.name}'
```

### Asyncio

Just request the `asio_grpc_stub` fixture in an `async def` test.

```python
@pytest.mark.asyncio
async def test_some_async(aio_grpc_stub):
    request = EchoRequest()
    response = await aio_grpc_stub.handler(request)
    assert response.name == f'test-{request.name}'
```

For a full example, see [`pytest_grpc/tests/test_api.py`](pytest_grpc/tests/test_api.py).

### SSL credentials

Just define the fixtures `grpc_server_credentials`, and `ssl_channel_credentials`

```python
@pytest.fixture
def grpc_server_credentials(key, cert):
    return grpc.ssl_server_credentials([
        (key, cert),
    ])


@pytest.fixture
def grpc_channel_credentials(cert):
    return grpc.ssl_channel_credentials(cert)
```

For a full example, see [`pytest_grpc/tests/test_ssl.py`](pytest_grpc/tests/test_ssl.py).

## Examples

See the [`pytest_grpc/tests/`](pytest_grpc/tests/) directory.
