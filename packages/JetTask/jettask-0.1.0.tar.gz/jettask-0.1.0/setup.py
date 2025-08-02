#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import re

# 读取版本号
def get_version():
    with open(os.path.join("jettask", "__init__.py"), "r", encoding="utf-8") as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")

# 读取 README
def get_long_description():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# 读取依赖
def get_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="JetTask",
    version=get_version(),
    author="yuyang",
    author_email="1194681498@qq.com",
    description="基于asyncio和Redis Stream的高性能分布式任务队列系统",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/qiyuebuku/easy-task",
    packages=find_packages(exclude=["examples*", "tests*", "docs*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=get_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jettask=jettask.webui.run:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="asyncio redis task-queue distributed celery",
    project_urls={
        "Bug Reports": "https://github.com/qiyuebuku/easy-task/issues",
        "Source": "https://github.com/qiyuebuku/easy-task",
    },
)