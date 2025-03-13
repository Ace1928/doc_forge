#!/usr/bin/env python3
# 🌀 Eidosian Documentation System - Module Entry Point
"""
Doc Forge - Module Entry Point

This module serves as the entry point when doc_forge is executed as a module
with `python -m doc_forge`. It follows Eidosian principles of seamless flow
and minimal friction, redirecting to the appropriate command interface.
"""

import sys
from pathlib import Path

def main():
    """Module entry point with seamless command redirection."""
    try:
        # First try importing and using the doc_forge.run module
        from .run import main as run_main
        sys.exit(run_main())
    except ImportError:
        # Fall back to the doc_forge module if run.py is not available
        from .doc_forge import main as forge_main
        sys.exit(forge_main())
    except Exception as e:
        print(f"❌ Error executing doc_forge: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
