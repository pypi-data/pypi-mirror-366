from setuptools import setup, find_packages

setup(
    name="uuid7gen",
    version="0.1.0",
    description="A package for generating and benchmarking UUIDv7.",
    author="Chowlett2",
    license="MIT",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.7",
    include_package_data=True,
    url="",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
