#!/usr/bin/env python3
"""
Setup script for NeuraX AI Tool
Author: Alex Butler [Vritra Security Organization]
Version: 1.0.0
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_long_description():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="neurax-ai",
    version="1.0.0",
    author="Alex Butler",
    description="A powerful CLI and Telegram bot interface for Perplexity AI",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/VritraSecz/NeuraX",
    project_urls={
        "Bug Tracker": "https://github.com/VritraSecz/NeuraX/issues",
        "Documentation": "https://github.com/VritraSecz/NeuraX/blob/main/README.md",
        "Source Code": "https://github.com/VritraSecz/NeuraX",
        "Developer Website": "https://vritrasec.com",
        "Telegram Channel": "https://t.me/VritraSec",
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "neurax=neurax.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="ai, chatbot, telegram, cli, perplexity, assistant, neurax",
    python_requires=">=3.7",
    zip_safe=False,
)
