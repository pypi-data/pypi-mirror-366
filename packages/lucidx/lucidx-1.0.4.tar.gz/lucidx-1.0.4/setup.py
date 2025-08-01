#!/usr/bin/env python3
"""
Setup script for LucidX - AI-Powered Image Synthesis Engine
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

# Read requirements
requirements = []
if os.path.exists("requirements.txt"):
    with open("requirements.txt", "r") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="lucidx",
    version="1.0.4",
    author="Alex Butler [Vritra Security Organization]",
    description="AI-powered image synthesis engine using Stability AI API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VritraSecz/LucidX",
    project_urls={
        "Bug Tracker": "https://github.com/VritraSecz/LucidX/issues",
        "Documentation": "https://github.com/VritraSecz/LucidX#readme",
        "Source Code": "https://github.com/VritraSecz/LucidX",
        "Telegram": "https://t.me/LinkCentralX",
        "Website": "https://vritrasec.com",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Artistic Software",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    python_requires=">=3.7",
    install_requires=[
        "colorama>=0.4.4",
        "requests>=2.25.1",
        "pathlib2>=2.3.0;python_version<'3.4'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "twine>=3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lucidx=lucidx.main:main",
        ],
    },
    keywords=[
        "ai", "artificial-intelligence", "image-generation", "stability-ai", 
        "text-to-image", "image-synthesis", "cli", "tool", "python",
        "machine-learning", "deep-learning", "creative", "art", "digital-art"
    ],
    license="MIT",
    include_package_data=True,
    zip_safe=False,
    platforms=['any'],
)
