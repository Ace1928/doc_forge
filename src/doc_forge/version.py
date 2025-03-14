#!/usr/bin/env python3
# 🌀 Eidosian Version System - Single Source of Truth
"""
Version information for Doc Forge.

This module provides a single source of truth for version information
across the entire Doc Forge system. It follows Eidosian principles of
precision, structure, and universal applicability.
"""

import os
import re
from pathlib import Path
from typing import Dict, Tuple, Union, Optional, Any

# Version components with Eidosian precision
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_LABEL = ""  # Can be "alpha", "beta", "rc", etc.
VERSION_LABEL_NUM = 0  # For alpha.1, beta.2, etc.

# Assembled version information - the core truth
VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
if VERSION_LABEL:
    VERSION += f"-{VERSION_LABEL}"
    if VERSION_LABEL_NUM > 0:
        VERSION += f".{VERSION_LABEL_NUM}"

# PEP 440 compatible version for setuptools
PEP440_VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
if VERSION_LABEL:
    if VERSION_LABEL == "alpha":
        PEP440_VERSION += f"a{VERSION_LABEL_NUM}" if VERSION_LABEL_NUM > 0 else "a0"
    elif VERSION_LABEL == "beta":
        PEP440_VERSION += f"b{VERSION_LABEL_NUM}" if VERSION_LABEL_NUM > 0 else "b0"
    elif VERSION_LABEL == "rc":
        PEP440_VERSION += f"rc{VERSION_LABEL_NUM}" if VERSION_LABEL_NUM > 0 else "rc0"
    else:
        PEP440_VERSION += f".{VERSION_LABEL}{VERSION_LABEL_NUM}" if VERSION_LABEL_NUM > 0 else f".{VERSION_LABEL}"

def get_version_string() -> str:
    """
    Get the full version string with Eidosian clarity.
    
    Returns:
        Complete version string
    """
    return VERSION

def get_version_tuple() -> Tuple[int, int, int, str, int]:
    """
    Get the version components as a tuple.
    
    Returns:
        Tuple of (major, minor, patch, label, label_number)
    """
    return (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, VERSION_LABEL, VERSION_LABEL_NUM)

def get_version_info() -> Dict[str, Union[int, str]]:
    """
    Get complete version information as a dictionary.
    
    Returns:
        Dictionary with version components
    """
    return {
        "major": VERSION_MAJOR,
        "minor": VERSION_MINOR,
        "patch": VERSION_PATCH,
        "label": VERSION_LABEL,
        "label_num": VERSION_LABEL_NUM,
        "version": VERSION,
        "pep440_version": PEP440_VERSION
    }

def get_version_from_file() -> Optional[str]:
    """
    Get version from VERSION file if it exists.
    
    Returns:
        Version string from file or None if file doesn't exist
    """
    # Try to find VERSION file in common locations
    version_file_paths = [
        Path(__file__).resolve().parent.parent.parent / "VERSION",  # /repo/VERSION
        Path(__file__).resolve().parent.parent / "VERSION",         # /repo/src/VERSION
        Path(__file__).resolve().parent / "VERSION",                # /repo/src/doc_forge/VERSION
    ]
    
    for version_file in version_file_paths:
        if version_file.exists():
            with open(version_file, "r", encoding="utf-8") as f:
                return f.read().strip()
    
    return None

def update_version_from_env() -> None:
    """Update global version variables from environment variables."""
    global VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, VERSION_LABEL, VERSION_LABEL_NUM, VERSION, PEP440_VERSION
    
    if "DOC_FORGE_VERSION" in os.environ:
        version_str = os.environ["DOC_FORGE_VERSION"]
        
        # Parse version string with regex
        match = re.match(r"(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z]+)\.?(\d+)?)?", version_str)
        if match:
            groups = match.groups()
            VERSION_MAJOR = int(groups[0])
            VERSION_MINOR = int(groups[1])
            VERSION_PATCH = int(groups[2])
            VERSION_LABEL = groups[3] or ""
            VERSION_LABEL_NUM = int(groups[4]) if groups[4] else 0
            
            # Update assembled versions
            VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
            if VERSION_LABEL:
                VERSION += f"-{VERSION_LABEL}"
                if VERSION_LABEL_NUM > 0:
                    VERSION += f".{VERSION_LABEL_NUM}"
            
            # Update PEP440 version
            PEP440_VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
            if VERSION_LABEL:
                if VERSION_LABEL == "alpha":
                    PEP440_VERSION += f"a{VERSION_LABEL_NUM}" if VERSION_LABEL_NUM > 0 else "a0"
                elif VERSION_LABEL == "beta":
                    PEP440_VERSION += f"b{VERSION_LABEL_NUM}" if VERSION_LABEL_NUM > 0 else "b0"
                elif VERSION_LABEL == "rc":
                    PEP440_VERSION += f"rc{VERSION_LABEL_NUM}" if VERSION_LABEL_NUM > 0 else "rc0"
                else:
                    PEP440_VERSION += f".{VERSION_LABEL}{VERSION_LABEL_NUM}" if VERSION_LABEL_NUM > 0 else f".{VERSION_LABEL}"

# Check for version file or environment variable on module load
file_version = get_version_from_file()
if file_version:
    os.environ["DOC_FORGE_VERSION"] = file_version
    update_version_from_env()
else:
    update_version_from_env()

if __name__ == "__main__":
    print(f"Doc Forge v{VERSION} (PEP440: {PEP440_VERSION})")
    print(f"Version components: {get_version_tuple()}")
    print(f"Version info: {get_version_info()}")
