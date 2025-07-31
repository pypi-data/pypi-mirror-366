#!/usr/bin/env python3
"""
Smart Timeout MCP Server 배포용 설정
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="claude-progress-guardian-mcp",
    version="1.0.0",
    author="yscha88",
    author_email="clmfkilu@gmail.com",
    description="Prevents infinite progress bar spam in Claude Code with intelligent timeout management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yscha88/claude-progress-guardian-mcp",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.8",
    install_requires=[
        "asyncio",
        "dataclasses; python_version<'3.7'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "claude-progress-guardian=smart_timeout_mcp.cli:main",
            "progress-guardian-server=smart_timeout_mcp.server:run_server",
        ],
    },
    keywords="claude, code, progress, bar, spam, timeout, mcp, guardian, monitoring",
    project_urls={
        "Bug Reports": "https://github.com/yscha88/claude-progress-guardian-mcp/issues",
        "Source": "https://github.com/yscha88/claude-progress-guardian-mcp",
        "Documentation": "https://github.com/yscha88/claude-progress-guardian-mcp/wiki",
    },
)