#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JiaJia - RSA-AES混合加密框架
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="jiajia",
    version="1.1.0",
    author="夏云龙",
    author_email="1900098962@qq.com",
    description="轻量级RSA-AES混合加密框架",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/xiatian/jiajia",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "redis": ["redis>=4.0.0"],
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
        ],
    },
    keywords="encryption, cryptography, rsa, aes, hmac, security, hybrid",
    project_urls={
        "Bug Reports": "https://github.com/xiatian/jiajia/issues",
        "Source": "https://github.com/xiatian/jiajia",
        "Documentation": "https://github.com/xiatian/jiajia#readme",
    },
) 