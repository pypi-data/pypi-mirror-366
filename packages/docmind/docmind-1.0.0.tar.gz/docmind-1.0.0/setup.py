#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="docmind",
    version="1.0.0",
    author="Mount",
    author_email="simon@mount.agency",
    description="AI-optimized document converter for technical documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mount-agency/docmind",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing :: Markup",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Office Suites",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "docmind=docmind.__main__:cli_main",
        ],
    },
    extras_require={
        "full": ["tqdm>=4.64.0", "pytesseract>=0.3.10"],
        "ocr": ["pytesseract>=0.3.10"],
        "progress": ["tqdm>=4.64.0"],
    },
    keywords="pdf docx markdown converter ai llm technical documents",
    project_urls={
        "Bug Reports": "https://github.com/mount-agency/docmind/issues",
        "Source": "https://github.com/mount-agency/docmind",
        "Documentation": "https://github.com/mount-agency/docmind#readme",
    },
    include_package_data=True,
    zip_safe=False,
)