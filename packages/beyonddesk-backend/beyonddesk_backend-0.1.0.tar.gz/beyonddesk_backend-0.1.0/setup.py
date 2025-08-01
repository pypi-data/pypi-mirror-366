from setuptools import setup, find_packages

setup(
    name="beyonddesk_backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "grpcio>=1.66.2",
        "grpcio-tools>=1.66.2",
        "protobuf>=5.28.2",
    ],
    include_package_data=True,
    package_data={
        "beyonddesk_backend": ["proto/*.proto", "*.py"],
    },
    author="Maruthi",
    author_email="maruthi@beyonddesk.com",
    description="gRPC service definitions for BackEnd",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/beyond-desk/grpc-service",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)