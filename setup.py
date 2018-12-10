from setuptools import setup, find_packages

install_requires = ["pytest>=3.6.0"]


setup(
    name="pytest-grpc",
    license="MIT",
    author="Denis Kataev",
    author_email="denis.a.kataev@gmail.com",
    url="",
    platforms=["linux", "osx", "win32"],
    packages=find_packages(),
    entry_points={
        "pytest11": ["pytest_grpc = pytest_grpc.plugin"]
    },
    zip_safe=False,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
