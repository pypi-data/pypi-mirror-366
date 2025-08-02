#!/usr/bin/python3
from setuptools import setup

# METADATA
NAME = "mcts-simple"
VERSION = "1.1.0"
AUTHOR = "Lance Chin"
EMAIL = "denselance@gmail.com"
DESCRIPTION = "mcts-simple is a Python3 library that implements Monte Carlo Tree Search and its variants to solve a host of problems, most commonly for reinforcement learning."
URL = "https://github.com/DenseLance/mcts-simple"
REQUIRES_PYTHON = ">=3.8.0"

DEPENDENCIES = ["tqdm", "msgpack"]

with open("README.md", "r", encoding = "utf-8") as f:
    long_description = f.read()
    f.close()

setup(
    name = NAME,
    version = VERSION,
    author = AUTHOR,
    author_email = EMAIL,
    description = DESCRIPTION,
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = URL,
    project_urls = {
        "Bug Tracker": "https://github.com/DenseLance/mcts-simple/issues",
    },
    license = "MIT",
    classifiers = [
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    packages = ["mcts_simple", "mcts_simple.mcts"],
    python_requires = REQUIRES_PYTHON,
    install_requires = DEPENDENCIES
)
