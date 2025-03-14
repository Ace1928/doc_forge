#!/usr/bin/env python3
# 🌀 Eidosian Command Runner
"""
Command Runner Module - Unified Entry Point for All Operations

This module provides the central entry point for all Doc Forge commands,
organizing and unifying the command structure following Eidosian principles
of structure, flow, clarity, and precision.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Any, Callable, Tuple, Union

# Core command imports
from .doc_forge import create_parser as create_doc_forge_parser
from .doc_forge import main as doc_forge_main
from .test_command import add_test_subparsers
from .version import get_version_string

# 📊 Self-aware logging system
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
)
logger = logging.getLogger("doc_forge")

def main() -> int:
    """
    Main entry point for Doc Forge command-line interface.
    
    Returns:
        Exit code (0 for success)
    """
    # Create the argument parser
    parser = create_main_parser()
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Set debug mode if requested
    if hasattr(args, "debug") and args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Print version if requested
    if hasattr(args, "version") and args.version:
        print(f"Doc Forge v{get_version_string()}")
        return 0
    
    # Determine the command type
    if hasattr(args, "command_type"):
        if args.command_type == "docs":
            return doc_forge_main()
        elif args.command_type == "test":
            if hasattr(args, "func"):
                return args.func(args)
            else:
                parser.parse_args(["test", "--help"])
                return 0
    
    # If no command type or direct command, delegate to doc_forge_main
    try:
        return doc_forge_main()
    except Exception as e:
        logger.error(f"❌ Command execution failed: {e}")
        if logging.getLogger().level <= logging.DEBUG:
            import traceback
            logger.debug(traceback.format_exc())
        return 1

def create_main_parser() -> argparse.ArgumentParser:
    """
    Create the main argument parser with all subcommands.
    
    Returns:
        Configured argparse.ArgumentParser instance
    """
    # Create the main parser
    parser = argparse.ArgumentParser(
        description="🌀 Doc Forge - Universal Documentation System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add version and debug arguments
    parser.add_argument(
        "--version", "-V", action="store_true",
        help="Show version information and exit"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable debug logging"
    )
    
    # Create subparsers for different command types
    subparsers = parser.add_subparsers(dest="command_type", help="Command type")
    
    # Documentation commands
    docs_parser = subparsers.add_parser(
        "docs", help="Documentation commands"
    )
    docs_subparser = docs_parser.add_subparsers(dest="command", help="Documentation command")
    create_doc_forge_parser(docs_parser)
    
    # Test commands
    test_parser = subparsers.add_parser(
        "test", help="Test commands"
    )
    test_subparsers = test_parser.add_subparsers(dest="command", help="Test command")
    add_test_subparsers(test_subparsers)
    
    return parser

if __name__ == "__main__":
    sys.exit(main())
