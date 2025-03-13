#!/usr/bin/env python3
# 🌀 Eidosian Documentation System - Central Package Interface
"""
Doc Forge - Universal Documentation Management System

This package integrates a suite of documentation tools built on
Eidosian principles of structure, flow, precision, and self-awareness.
Each component is designed for surgical precision and architectural elegance.
"""

# Core path utilities - foundation of structure
from .utils.paths import get_repo_root, get_docs_dir, resolve_path, ensure_dir

# Documentation management components
from .update_toctrees import update_toctrees
from .fix_inline_refs import fix_inline_references
from .doc_validator import validate_docs
from .doc_toc_analyzer import analyze_toc
from .doc_manifest_manager import load_doc_manifest

# CLI functions for direct access
try:
    from .run import main as run_cli
except ImportError:
    from .doc_forge import main as run_cli

__version__ = "1.0.0"

# Core execution entry points
def main():
    """Command-line entry point for direct script execution."""
    return run_cli()

def forge_docs(docs_dir=None, fix_toc=True, fix_refs=True, validate=True):
    """
    One-shot function to update and fix documentation.
    
    Args:
        docs_dir: Documentation directory (auto-detected if None)
        fix_toc: Whether to fix table of contents issues
        fix_refs: Whether to fix inline references
        validate: Whether to validate documentation
        
    Returns:
        True if all operations succeeded, False otherwise
    """
    # Resolve docs directory
    if docs_dir is None:
        docs_dir = get_docs_dir()
    
    success = True
    
    # Run requested operations
    if fix_toc:
        toc_result = update_toctrees(docs_dir)
        success = success and (toc_result >= 0)
        
    if fix_refs:
        refs_result = fix_inline_references(docs_dir)
        success = success and (refs_result >= 0)
        
    if validate:
        discrepancies = validate_docs(get_repo_root())
        success = success and not discrepancies
        
    return success
