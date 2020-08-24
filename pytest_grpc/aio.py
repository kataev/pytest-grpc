import socket
from concurrent import futures

from grpc.experimental import aio
import grpc
import pytest
import asyncio
import nest_asyncio as _nest_asyncio


# async Server fixtures

@pytest.fixture
def aio_grpc_server(event_loop, grpc_addr, grpc_add_to_server, grpc_servicer, grpc_interceptors):
    async def run(server):
        await server.start()

    async def stop(server):
        await server.stop(grace=None)

    server = aio.server(interceptors=grpc_interceptors)
    grpc_add_to_server(grpc_servicer(), server)
    server.add_insecure_port(grpc_addr)
    event_loop.run_until_complete(run(server))
    yield server
    event_loop.run_until_complete(stop(server))


# asyncio Client fixtures

@pytest.fixture
def aio_grpc_create_channel(request, grpc_addr):
    return aio.insecure_channel(grpc_addr)


@pytest.mark.asyncio
@pytest.fixture
async def aio_grpc_channel(event_loop, aio_grpc_create_channel):
    async with aio_grpc_create_channel as channel:
        yield channel


@pytest.fixture
def aio_grpc_stub(grpc_stub_cls, aio_grpc_channel):
    return grpc_stub_cls(aio_grpc_channel)
