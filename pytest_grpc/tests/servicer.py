from .example_pb2 import EchoRequest, EchoResponse, Empty
from .example_pb2_grpc import EchoServiceServicer
import threading


class Servicer(EchoServiceServicer):
    def __init__(self):
        self.barrier = threading.Barrier(2)

    def handler(self, request: EchoRequest, context) -> EchoResponse:
        return EchoResponse(name=f'test-{request.name}')

    def error_handler(self, request: EchoRequest, context) -> EchoResponse:
        raise RuntimeError('Some error')

    def blocking(self, request_stream, context):
        for i in range(2):
            yield EchoResponse(name=str(i))
            self.barrier.wait()

    def unblock(self, _, context):
        self.barrier.wait()
        return Empty()
