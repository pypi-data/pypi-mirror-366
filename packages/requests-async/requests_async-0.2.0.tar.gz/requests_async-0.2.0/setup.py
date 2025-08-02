from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="requests-async",  # Replace with your package name
    version="0.2.0",
    author="taisui",
    author_email="tais00@qq.com",
    description="An asynchronous HTTP request library based on httpx.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/taisuii/requests-async",  # Replace with your project URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "httpx",
        "loguru"
    ],
)