#!/usr/bin/env python3
"""
Setup script for pocketflow-agui
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "PocketFlow的AGUI扩展版本 - 支持前端事件回调的轻量级工作流编排框架"

setup(
    name="pocketflow-agui",
    version="0.1.0",
    author="AGUI Team",
    author_email="agui@example.com",
    description="PocketFlow的AGUI扩展版本 - 支持前端事件回调的轻量级工作流编排框架",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pocketflow-agui",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/pocketflow-agui/issues",
        "Documentation": "https://github.com/yourusername/pocketflow-agui/blob/main/README.md",
        "Source Code": "https://github.com/yourusername/pocketflow-agui",
    },
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typing-extensions>=4.0.0; python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
            "pytest-asyncio",
            "black",
            "isort",
            "flake8",
            "mypy",
            "pre-commit",
        ],
    },
    keywords=["workflow", "orchestration", "agui", "frontend", "events"],
    include_package_data=True,
    zip_safe=False,
)
