#!/usr/bin/env python3
# 🌀 Eidosian Documentation System - Module Entry Point
"""
Doc Forge - Module Entry Point

This module serves as the entry point when doc_forge is executed as a module
with `python -m doc_forge`. It follows Eidosian principles of seamless flow
and minimal friction, redirecting to the appropriate command interface.
"""

import sys
import argparse
import logging
from pathlib import Path

def main():
    """Module entry point with seamless command redirection."""
    # Create the main parser
    parser = argparse.ArgumentParser(
        description="🌀 Doc Forge - Universal Documentation Management System"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Update TOCTrees command
    toc_parser = subparsers.add_parser("toc", help="Update table of contents trees")
    toc_parser.add_argument("docs_dir", nargs='?', type=Path, default=None, 
                           help="Documentation directory (default: auto-detect)")
    
    # Fix inline references command
    refs_parser = subparsers.add_parser("refs", help="Fix inline references")
    refs_parser.add_argument("docs_dir", nargs='?', type=Path, default=None, 
                            help="Documentation directory (default: auto-detect)")
    
    # Validate docs command
    validate_parser = subparsers.add_parser("validate", help="Validate documentation")
    validate_parser.add_argument("repo_path", nargs='?', type=Path, default=None,
                               help="Repository path (default: auto-detect)")
    
    # Add test subcommands
    try:
        from .test_command import add_test_subparsers
        test_parser = subparsers.add_parser("test", help="Test-related commands")
        test_subparsers = test_parser.add_subparsers(dest="test_command", help="Test command to execute")
        add_test_subparsers(test_subparsers)
    except ImportError as e:
        print(f"Warning: Test commands not available: {e}")
    
    # Add global debugging option
    parser.add_argument('--debug', action='store_true', 
                      help='Enable debug logging')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Enable debug logging if requested
    if getattr(args, 'debug', False):
        logging.basicConfig(level=logging.DEBUG)
    
    # Route to the appropriate command
    try:
        if args.command == "toc":
            from .update_toctrees import update_toctrees
            result = update_toctrees(args.docs_dir)
            sys.exit(0 if result >= 0 else 1)
            
        elif args.command == "refs":
            from .fix_inline_refs import fix_inline_references
            result = fix_inline_references(args.docs_dir)
            sys.exit(0 if result >= 0 else 1)
            
        elif args.command == "validate":
            from .doc_validator import validate_docs
            discrepancies = validate_docs(args.repo_path)
            sys.exit(1 if discrepancies else 0)
            
        elif args.command == "test" and hasattr(args, "test_command") and args.test_command:
            # Execute the appropriate test subcommand
            if hasattr(args, "func"):
                result = args.func(args)
                sys.exit(result)
            else:
                print("No test subcommand specified. Available subcommands:")
                print("  analyze - Analyze test coverage")
                print("  todo    - Generate test TODO document")
                print("  stubs   - Generate test stubs")
                print("  suite   - Generate test suite")
                print("  run     - Run tests")
                sys.exit(1)
            
        else:
            # Default to the main CLI if no command specified or no args
            from .run import main as run_main
            sys.exit(run_main())
                
    except ImportError as e:
        print(f"❌ Error importing module: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
