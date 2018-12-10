Compile with:

```bash
pip install grpcio grpcio-tools
python -m grpc_tools.protoc -Isrc --python_out=src/stub --grpc_python_out=src/stub src/test.proto
PYTHONPATH=src py.test
# or
PYTHONPATH=src py.test --grpc-fake-server
```
