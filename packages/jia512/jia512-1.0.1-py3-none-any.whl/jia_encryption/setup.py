#!/usr/bin/env python3
"""
Jia - 轻量级加密解密框架
一个通用的RSA-AES混合加密框架，提供RSA非对称加密、AES对称加密、HMAC签名验证等功能。
"""

import os
from setuptools import setup, find_packages

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements文件
def read_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return requirements

setup(
    name="jia-encryption",
    version="1.1.0",
    author="夏云龙",
    author_email="xiayunlong@example.com",
    description="轻量级加密解密框架，提供RSA-AES混合加密功能",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/xiayunlong/jia-encryption",
    project_urls={
        "Bug Reports": "https://github.com/xiayunlong/jia-encryption/issues",
        "Source": "https://github.com/xiayunlong/jia-encryption",
        "Documentation": "https://github.com/xiayunlong/jia-encryption/blob/main/README.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.7",
    install_requires=[
        "cryptography>=3.4.8",
    ],
    extras_require={
        "redis": ["redis>=4.0.0"],
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
            "twine>=3.4.0",
            "wheel>=0.37.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    keywords="encryption, cryptography, rsa, aes, hmac, security, async",
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "jia=jia.cli:main",
        ],
    },
) 