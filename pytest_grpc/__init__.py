import pytest
import grpc
import packaging.version

__version__ = '0.8.0'

aio_available = pytest.mark.skipif(
    packaging.version.parse(grpc.__version__) < packaging.version.parse("1.31.0"),
    reason="aio test only work with grpcio versions 1.31.0 and later"
)
