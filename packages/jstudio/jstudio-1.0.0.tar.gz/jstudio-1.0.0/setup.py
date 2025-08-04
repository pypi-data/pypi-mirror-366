#!/usr/bin/env python3
"""Setup script for the JStudio Python SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jstudio",
    version="1.0.0",
    author="JStudio",
    author_email="contact@joshlei.com",
    description="Official Python SDK for JStudio's API & WebSocket services - Fast, reliable API for real-time data from Various Games (Roblox)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JStudiooo/growagarden-api",
    project_urls={
        "Bug Tracker": "https://discord.gg/kCryJ8zPwy",
        "Homepage": "https://api.joshlei.com",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords=[
        "jstudio",
        "grow-a-garden", 
        "roblox",
        "api",
        "sdk",
        "gaming",
        "real-time"
    ],
    include_package_data=True,
    zip_safe=False,
)
