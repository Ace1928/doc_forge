#!/usr/bin/env python3
# 🌀 Eidosian Module Entry Point
"""
Module Entry Point - For Direct Module Execution

This module serves as the entry point when Doc Forge is executed
directly as a module using 'python -m doc_forge'.

Following Eidosian principles of:
- Velocity as Intelligence: Direct path to execution
- Structure as Control: Clear entry point architecture
- Self-Awareness: Understanding execution context
"""

import sys
from .run import main

if __name__ == "__main__":
    # Pass control to the main runner
    sys.exit(main())
