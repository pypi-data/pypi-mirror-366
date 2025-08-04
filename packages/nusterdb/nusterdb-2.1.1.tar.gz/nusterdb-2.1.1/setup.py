#!/usr/bin/env python3
"""
NusterDB Python Package Setup
=============================

A high-performance, government-grade vector database with FAISS-compatible algorithms.
"""

from setuptools import setup, find_packages
from pathlib import Path
import os
import platform
import subprocess

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Version
VERSION = "2.1.1"

def get_platform_specific_args():
    """Get platform-specific compilation arguments"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    compile_args = ["-std=c++17", "-O3"]
    link_args = []
    
    if system == "darwin":  # macOS
        if "arm" in machine or "aarch64" in machine:
            # Apple Silicon
            compile_args.extend(["-arch", "arm64", "-mmacosx-version-min=11.0"])
            link_args.extend(["-arch", "arm64"])
        else:
            # Intel Mac
            compile_args.extend(["-arch", "x86_64", "-mmacosx-version-min=10.14"])
            link_args.extend(["-arch", "x86_64"])
    elif system == "linux":
        compile_args.extend(["-fPIC", "-march=native"])
        if "aarch64" in machine:
            compile_args.append("-mcpu=native")
    elif system == "windows":
        # Windows-specific flags
        compile_args = ["/std:c++17", "/O2", "/DWIN32", "/D_WIN32_WINNT=0x0601"]
        link_args = []
    
    return compile_args, link_args

# Get platform-specific arguments
compile_args, link_args = get_platform_specific_args()

# For now, we'll use pure Python implementation
# C++ extensions will be added in future versions
ext_modules = []

setup(
    name="nusterdb",
    version=VERSION,
    author="NusterAI Team",
    author_email="info@nusterai.com",
    description="High-performance, government-grade vector database with FAISS-compatible algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NusterAI/nusterdb",
    project_urls={
        "Bug Tracker": "https://github.com/NusterAI/nusterdb/issues",
        "Documentation": "https://docs.nusterai.com/nusterdb",
        "Source Code": "https://github.com/NusterAI/nusterdb",
    },
    packages=find_packages(),
    ext_modules=ext_modules,
    install_requires=[
        "numpy>=1.20.0",
        "requests>=2.25.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-benchmark>=3.4.0",
            "black>=21.0.0",
            "mypy>=0.900",
            "pre-commit>=2.15.0",
        ],
        "benchmark": [
            "faiss-cpu>=1.7.0",
            "matplotlib>=3.5.0",
            "pandas>=1.5.0",
        ],
        "server": [
            "uvicorn>=0.15.0",
            "fastapi>=0.68.0",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: GPU :: NVIDIA CUDA",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
    ],
    python_requires=">=3.8",
    keywords="vector database, similarity search, machine learning, AI, FAISS, government-grade, security",
    zip_safe=False,
    # cmdclass={"build_ext": build_ext},  # Disabled for pure Python version
)