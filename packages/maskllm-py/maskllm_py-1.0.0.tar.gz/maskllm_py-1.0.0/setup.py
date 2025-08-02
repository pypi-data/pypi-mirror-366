"""Setup tools"""
import os

from setuptools import setup

# pylint: disable=W1501,W1514
with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

setup(
    name="maskllm_py",
    version="1.0.0",
    author="MaskLLM Developers",
    author_email="admin@maskllm.com",
    description="Python SDK for MaskLLM",
    # flake8: noqa
    url="https://github.com/mwpnava/Python-Code/tree/master/My_own_Python_package",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    py_modules=["maskllm_py/resolver"],
)
