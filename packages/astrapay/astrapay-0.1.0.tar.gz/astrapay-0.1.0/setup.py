# setup.py

from setuptools import setup, find_packages

setup(
    name="astrapay",
    version="0.1.0",
    description="Lightweight Python SDK for M-Pesa STK Push by Astra Softwares",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ishmael Bett",
    author_email="info.astrasoft@gmail.com",
    url="https://github.com/astrasoft/astrapay",  # replace with actual URL
    license="MIT",
    packages=find_packages(),
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
    ],
    python_requires='>=3.6',
)
