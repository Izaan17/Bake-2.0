#!/usr/bin/env python3
"""
Setup script for Bake - Python Script Command Manager
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
    name="bake-command-manager",
    version="1.0.0",
    author="Izaan Noman",
    author_email="your.email@example.com",
    description="A tool for managing custom Python script commands",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Izaan17/Bake-2.0",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "bake=bake:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="command-line, python, scripts, shell, utilities, automation",
    project_urls={
        "Bug Reports": "https://github.com/Izaan17/Bake-2.0/issues",
        "Source": "https://github.com/Izaan17/Bake-2.0",
        "Documentation": "https://github.com/Izaan17/Bake-2.0#readme",
    },
)
