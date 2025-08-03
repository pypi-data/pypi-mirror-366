"""Setup configuration for TaskPriority MCP Server."""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="taskpriority-mcp",
    version="1.0.0",
    author="TaskPriority Team",
    author_email="support@taskpriority.ai",
    description="MCP server for intelligent task prioritization with Claude Desktop",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcp-priority",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/mcp-priority/issues",
        "Documentation": "https://github.com/yourusername/mcp-priority#readme",
        "Source Code": "https://github.com/yourusername/mcp-priority",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "taskpriority-mcp=src.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords="mcp claude taskpriority ai task-management",
)