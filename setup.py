from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pytest-grpc",
    license="MIT",
    version='0.8.0',
    author="Denis Kataev",
    author_email="denis.a.kataev@gmail.com",
    url="https://github.com/kataev/pytest-grpc",
    platforms=["linux", "osx", "win32"],
    packages=find_packages(),
    entry_points={
        "pytest11": ["pytest_grpc = pytest_grpc.plugin"]
    },
    description='pytest plugin for grpc',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "pytest>=3.6.0",
        "grpcio",
        "grpcio-tools",
    ],
    extras_require={
        "asyncio": [
            "grpcio>=1.31.0",
            "grpcio-tools>=1.31.0",
            "pytest-asyncio",
        ]
    },
    classifiers=[
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
