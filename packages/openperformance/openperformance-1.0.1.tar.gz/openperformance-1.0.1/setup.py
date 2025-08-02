#!/usr/bin/env python
"""Setup script for OpenPerformance ML Platform."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openperformance",
    version="1.0.0",
    author="Nik Jois",
    author_email="nik@llamasearch.ai",
    description="Enterprise ML Performance Engineering Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/llamasearchai/OpenPerformance",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "typer[all]>=0.9.0",
        "redis>=5.0.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.12.0",
        "numpy>=1.24.0",
        "pandas>=2.1.0",
        "torch>=2.1.0",
        "psutil>=5.9.0",
        "rich>=13.6.0",
        "prometheus-client>=0.19.0",
        "openai>=1.20.0",
        "shell-gpt>=1.0.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.6",
        "slowapi>=0.1.9",
        "argon2-cffi>=23.1.0",
        "pyotp>=2.9.0",
        "aiofiles>=23.2.0",
        "httpx>=0.25.0",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.9.0",
            "isort>=5.12.0",
            "mypy>=1.6.0",
            "flake8>=6.1.0",
            "pylint>=3.0.0",
            "pre-commit>=3.6.0",
            "tox>=4.0.0",
            "hatch>=1.9.0",
        ],
        "gpu": [
            "nvidia-ml-py>=12.535.0",
            "pynvml>=11.5.0",
            "GPUtil>=1.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mlperf=mlperf.cli.main:app",
            "openperf=mlperf.cli.main:app",
        ],
    },
)