#!/usr/bin/env python3
"""Setup script for bashimu package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="bashimu",
    version="1.2.0",
    author="Wiktor Lukasik",
    description="A command-line tool to interact with LLMs for bash and Linux questions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wiktorjl/bashimu",
    packages=find_packages(),
    py_modules=["tui.tui"],
    include_package_data=True,
    install_requires=[
        "prompt_toolkit",
        "openai",
        "requests",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "bashimu-tui=tui.tui:main",
        ],
    },
    scripts=[
        "bashimu.sh",
        "bashimu_setup.sh",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    keywords="bash linux cli chatgpt openai llm terminal",
)