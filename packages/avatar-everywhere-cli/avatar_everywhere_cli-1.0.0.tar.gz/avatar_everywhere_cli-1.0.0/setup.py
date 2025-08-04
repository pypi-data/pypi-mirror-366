#!/usr/bin/env python3
"""
Setup script for Avatar Everywhere CLI
Portable Sandbox Identity Toolkit
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="avatar-everywhere-cli",
    version="1.0.0",
    author="Abdulkareem Oyeneye/Dapps over Apps.",
    author_email="team@dappsoverapps.com",
    description="Portable Sandbox Identity Toolkit - NFT verification and VRM avatar conversion",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Supercoolkayy/avatar-everywhere-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "black>=23.9.1",
            "isort>=5.12.0",
            "mypy>=1.6.1",
            "memory-profiler>=0.61.0",
            "psutil>=5.9.0",
        ],
        "performance": [
            "memory-profiler>=0.61.0",
            "psutil>=5.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "avatar-everywhere=main:main",
            "avatar-cli=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords="sandbox avatar nft vrm metaverse polygon walletconnect",
    project_urls={
        "Bug Reports": "https://github.com/Supercoolkayy/avatar-everywhere-cli/issues",
        "Source": "https://github.com/Supercoolkayy/avatar-everywhere-cli",
        "Documentation": "https://github.com/Supercoolkayy/avatar-everywhere-cli#readme",
    },
) 