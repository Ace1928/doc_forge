#!/usr/bin/env python3
# 🌀 Eidosian Test Configuration
"""
Pytest configuration for Doc Forge tests.

This module provides common fixtures and configuration for all pytest-based tests
following Eidosian principles of structure and reusability.
"""

import pytest
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Ensure repository root is in path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔍 Path Fixtures - Perfect Control of Test Environments
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@pytest.fixture
def repo_root():
    """Return the repository root path."""
    return REPO_ROOT

@pytest.fixture
def src_dir():
    """Return the source directory path."""
    return REPO_ROOT / "src"

@pytest.fixture
def docs_dir():
    """Return the docs directory path."""
    return REPO_ROOT / "docs"

@pytest.fixture
def temp_dir():
    """Provide a temporary directory that is cleaned up after the test."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Cleanup after test
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_docs_dir(temp_dir):
    """Create a sample docs directory structure for testing."""
    docs_dir = temp_dir / "docs"
    docs_dir.mkdir()
    
    # Create some sample files
    index_md = docs_dir / "index.md"
    index_md.write_text("# Sample Documentation\n\nThis is a test document.")
    
    # Create subdirectories
    guides_dir = docs_dir / "guides"
    guides_dir.mkdir()
    guide_md = guides_dir / "sample_guide.md"
    guide_md.write_text("# Sample Guide\n\nThis is a sample guide document.")
    
    return docs_dir

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 Import Fixtures - Dynamic Module Loading for Testing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@pytest.fixture
def doc_forge():
    """Import and return the doc_forge module."""
    import doc_forge
    return doc_forge

@pytest.fixture
def ast_scanner():
    """Import and return the ast_scanner module."""
    sys.path.insert(0, str(REPO_ROOT / "tests"))
    try:
        import ast_scanner
        return ast_scanner
    except ImportError:
        pytest.skip("ast_scanner module not available")
