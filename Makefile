.PHONY: clean
clean:
	-rm -rf build dist *.egg-info htmlcov .eggs

.PHONY: minor
minor:
	bumpversion minor

.PHONY: major
major:
	bumpversion major

.PHONY: patch
patch:
	bumpversion patch

.PHONY: protos
protos:
	python -m grpc_tools.protoc -Iprotos --python_out=pytest_grpc/tests/ --grpc_python_out=pytest_grpc/tests/ pytest_grpc/tests/example.proto

.PHONY: publish
publish: protos
	pip3 install wheel twine
	python setup.py sdist bdist_wheel
	twine upload dist/*

.PHONY: upload
upload: clean publish

.PHONY: certs
certs:
	openssl req -x509 -newkey rsa:4096 -nodes -subj '/CN=localhost' -keyout pytest_grpc/tests/test_ssl/key.pem -out pytest_grpc/tests/test_ssl/cert.pem -days 365
