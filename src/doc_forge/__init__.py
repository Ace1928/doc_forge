#!/usr/bin/env python3
# 🌀 Eidosian Documentation System - Central Package Interface
"""
Doc Forge - Universal Documentation Management System

This package integrates a suite of documentation tools built on
Eidosian principles of structure, flow, precision, and self-awareness.
Each component is designed for surgical precision and architectural elegance.
"""

from .update_toctrees import update_toctrees
from .fix_inline_refs import fix_inline_references
from .doc_validator import validate_docs
from .doc_toc_analyzer import analyze_toc
from .doc_manifest_manager import load_doc_manifest

__version__ = "1.0.0"
