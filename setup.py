#!/usr/bin/env python3
from setuptools import setup, find_packages
import os

# Read the long description from README.md
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except (FileNotFoundError, IOError):
    long_description = "Doc Forge - Universal Documentation Management System"

# Get version from package
version = {}
with open(os.path.join("src", "doc_forge", "__init__.py"), encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)
            break

setup(
    name="doc-forge",
    version=version.get("__version__", "1.0.0"),
    author="Lloyd Handyside",
    author_email="lloyd@example.com",
    description="Universal Documentation Management System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lloydhandyside/doc_forge",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "doc-forge=doc_forge:main",
        ],
    },
    scripts=["bin/doc-forge"],  # Add the direct executable script
    install_requires=[
        "sphinx>=4.5.0",
        "sphinx-rtd-theme>=1.0.0",
        "sphinx-copybutton>=0.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "flake8>=4.0.0",
            "black>=22.0.0",
        ],
    },
)
