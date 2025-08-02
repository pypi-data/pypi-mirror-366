from setuptools import setup, find_packages
import os


def read_long_description():
    """Read README.md for long description"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "gRPC protocol definitions for BeyondDesk backend services"


def read_requirements():
    """Read requirements"""
    return [
        "grpcio>=1.66.2",
        "grpcio-tools>=1.66.2",
        "protobuf>=5.28.2",
        "googleapis-common-protos>=1.65.0",
    ]


setup(
    name="beyonddesk-grpc-protocols",
    version="0.0.1a",
    author="Maruthi",
    author_email="maruthi@beyonddesk.com",
    description="gRPC protocol definitions for BeyondDesk backend services",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/beyond-desk/beyonddesk-grpc-protocols",

    packages=find_packages(),
    include_package_data=True,

    package_data={
        "beyonddesk_grpc": [
            "**/*.py",
            "**/*.proto",
        ],
    },

    install_requires=read_requirements(),

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],

    python_requires=">=3.8",

    keywords="grpc protobuf beyonddesk microservices",

    project_urls={
        "Bug Reports": "https://github.com/beyond-desk/beyonddesk-grpc-protocols/issues",
        "Source": "https://github.com/beyond-desk/beyonddesk-grpc-protocols",
    },
)
