import socket
from concurrent import futures

import grpc
import pytest
from grpc._cython.cygrpc import CompositeChannelCredentials, _Metadatum



from .fake import FakeServer, FakeRpcError, FakeContext, FakeChannel
from .fixtures import grpc_addr, grpc_interceptors, \
    grpc_max_workers, grpc_server, grpc_create_channel, grpc_channel, grpc_stub, thread_pool
from .aio import aio_grpc_server, aio_grpc_create_channel, aio_grpc_channel, aio_grpc_stub


def pytest_addoption(parser):
    parser.addoption('--grpc-fake-server', action='store_true', dest='grpc-fake')
    parser.addoption('--grpc-max-workers', type=int, dest='grpc-max-workers', default=2)
