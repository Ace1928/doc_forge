#!/usr/bin/env python3
# 🌀 Eidosian Test Command System
"""
Test Command System - Eidosian Test Integration

This module integrates and orchestrates the Eidosian test analysis and generation systems,
providing a unified interface for test discovery, coverage analysis, and test generation.

Following Eidosian principles of:
- Structure as Control: Perfect organization of test components
- Flow Like a River: Seamless transitions between test operations
- Precision as Style: Exact and comprehensive test analysis
- Self-Awareness: Deep understanding of the codebase's test state
"""

import os
import sys
import argparse
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from datetime import datetime

# Import path utilities
from .utils.paths import get_repo_root, resolve_path, ensure_dir

# 📊 Structured Logging - Self-Awareness Foundation
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("eidosian_tests.command")

class TestCommand:
    """
    Central command interface for Eidosian test operations.
    
    Like a maestro conducting a symphony, this class orchestrates all test-related
    operations with precision, flow, and structural integrity.
    """
    
    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize the test command system with repository root."""
        self.repo_root = repo_root or get_repo_root()
        self.src_dir = self.repo_root / "src"
        self.tests_dir = self.repo_root / "tests"
        
        # Ensure tests directory exists
        ensure_dir(self.tests_dir)
        
        # Try to import analyzer dynamically
        try:
            sys.path.insert(0, str(self.tests_dir))
            from ast_scanner import CodeEntityAnalyzer
            self.analyzer = CodeEntityAnalyzer(self.repo_root)
        except ImportError:
            logger.warning("⚠️ Could not import CodeEntityAnalyzer - test analysis disabled")
            self.analyzer = None
    
    def analyze(self, output_format: str = "markdown") -> Path:
        """
        Analyze the codebase for test coverage and quality.
        
        Args:
            output_format: Format for the analysis report ("markdown", "json", or "html")
            
        Returns:
            Path to the generated analysis report
        """
        if not self.analyzer:
            raise ImportError("CodeEntityAnalyzer not available - test analysis disabled")
            
        logger.info("🔍 Starting test coverage analysis")
        
        # Run analysis
        self.analyzer.discover_all_structures()
        self.analyzer.analyze_tests()
        
        # Generate report
        if output_format.lower() == "json":
            report_path = self.analyzer.export_to_json()
        elif output_format.lower() == "html":
            report_path = self.analyzer.visualize_coverage()
        else:  # Default to markdown
            report_path = self.analyzer.generate_coverage_report()
            
        logger.info(f"✅ Test analysis complete: {report_path}")
        return report_path
    
    def generate_todo(self) -> Path:
        """
        Generate a comprehensive test TODO document.
        
        Returns:
            Path to the generated TODO document
        """
        if not self.analyzer:
            raise ImportError("CodeEntityAnalyzer not available - test generation disabled")
            
        logger.info("📝 Generating test TODO document")
        
        # Run generation
        todo_path = self.analyzer.generate_todo_document()
        
        logger.info(f"✅ Test TODO document generated: {todo_path}")
        return todo_path
    
    def generate_stubs(self, module: Optional[str] = None) -> List[Path]:
        """
        Generate test stub files for untested code.
        
        Args:
            module: Optional module name to focus on
            
        Returns:
            List of paths to generated stub files
        """
        if not self.analyzer:
            raise ImportError("CodeEntityAnalyzer not available - stub generation disabled")
            
        logger.info(f"🧪 Generating test stubs{f' for {module}' if module else ''}")
        
        # Filter for specific module if requested
        if module:
            # Discover all items
            self.analyzer.discover_all_structures()
            
            # Filter for the specified module
            filtered_items = [
                item for item in self.analyzer.discovered_items
                if item["module_path"].startswith(module)
            ]
            
            # Temporarily replace the discovered items
            original_items = self.analyzer.discovered_items
            self.analyzer.discovered_items = filtered_items
            
            # Generate stubs
            stubs_info = self.analyzer.generate_test_stubs()
            
            # Restore original items
            self.analyzer.discovered_items = original_items
        else:
            # Generate all stubs
            stubs_info = self.analyzer.generate_test_stubs()
            
        logger.info(f"✅ Generated {len(stubs_info['generated_files'])} test stub files")
        return [Path(p) for p in stubs_info['generated_files']]
    
    def generate_suite(self) -> Path:
        """
        Generate a comprehensive test suite.
        
        Returns:
            Path to the generated test suite
        """
        if not self.analyzer:
            raise ImportError("CodeEntityAnalyzer not available - suite generation disabled")
            
        logger.info("🏗️ Generating comprehensive test suite")
        
        # Generate the suite
        suite_dir = self.analyzer.generate_test_suite()
        
        logger.info(f"✅ Test suite generated in: {suite_dir}")
        return suite_dir
    
    def run_tests(self, pattern: str = "test_*.py", verbose: bool = False) -> bool:
        """
        Run tests in the tests directory.
        
        Args:
            pattern: Test file pattern to match
            verbose: Whether to show detailed output
            
        Returns:
            True if all tests passed, False otherwise
        """
        logger.info(f"▶️ Running tests matching pattern: {pattern}")
        
        # Build pytest command
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add verbosity
        if verbose:
            cmd.append("-v")
            
        # Add pattern
        cmd.extend(["-k", pattern])
        
        # Run the tests
        process = subprocess.run(
            cmd,
            cwd=self.repo_root,
            stdout=subprocess.PIPE if not verbose else None,
            stderr=subprocess.PIPE if not verbose else None,
            text=True
        )
        
        success = process.returncode == 0
        
        if success:
            logger.info("✅ All tests passed")
        else:
            logger.error("❌ Some tests failed")
            
            # Show output if not verbose (verbose mode already showed it)
            if not verbose and process.stdout:
                logger.info(process.stdout)
                
        return success

def cmd_analyze(args: argparse.Namespace) -> int:
    """
    Command handler for test analysis.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success)
    """
    repo_root = args.repo_root
    output_format = args.format
    
    try:
        command = TestCommand(repo_root)
        report_path = command.analyze(output_format)
        print(f"Analysis report generated: {report_path}")
        return 0
    except Exception as e:
        logger.error(f"Error analyzing tests: {e}")
        return 1

def cmd_todo(args: argparse.Namespace) -> int:
    """
    Command handler for generating test TODO document.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success)
    """
    repo_root = args.repo_root
    
    try:
        command = TestCommand(repo_root)
        todo_path = command.generate_todo()
        print(f"Test TODO document generated: {todo_path}")
        return 0
    except Exception as e:
        logger.error(f"Error generating test TODO document: {e}")
        return 1

def cmd_stubs(args: argparse.Namespace) -> int:
    """
    Command handler for generating test stubs.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success)
    """
    repo_root = args.repo_root
    module = args.module
    
    try:
        command = TestCommand(repo_root)
        stub_files = command.generate_stubs(module)
        print(f"Generated {len(stub_files)} test stub files:")
        for stub_file in stub_files:
            print(f"  - {stub_file}")
        return 0
    except Exception as e:
        logger.error(f"Error generating test stubs: {e}")
        return 1

def cmd_suite(args: argparse.Namespace) -> int:
    """
    Command handler for generating a comprehensive test suite.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success)
    """
    repo_root = args.repo_root
    
    try:
        command = TestCommand(repo_root)
        suite_dir = command.generate_suite()
        print(f"Test suite generated in: {suite_dir}")
        return 0
    except Exception as e:
        logger.error(f"Error generating test suite: {e}")
        return 1

def cmd_run(args: argparse.Namespace) -> int:
    """
    Command handler for running tests.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for test failures)
    """
    repo_root = args.repo_root
    pattern = args.pattern
    verbose = args.verbose
    
    try:
        command = TestCommand(repo_root)
        success = command.run_tests(pattern, verbose)
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return 1

def add_test_subparsers(subparsers: argparse._SubParsersAction) -> None:
    """
    Add test-related subparsers to the main parser.
    
    Args:
        subparsers: Subparsers action from the main parser
    """
    # Test analysis command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze test coverage and quality')
    analyze_parser.add_argument('--format', choices=['markdown', 'json', 'html'], default='markdown',
                               help='Output format for analysis report')
    analyze_parser.add_argument('--repo-root', type=Path, default=None,
                               help='Repository root directory (auto-detected if None)')
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Test TODO command
    todo_parser = subparsers.add_parser('todo', help='Generate a comprehensive test TODO document')
    todo_parser.add_argument('--repo-root', type=Path, default=None,
                            help='Repository root directory (auto-detected if None)')
    todo_parser.set_defaults(func=cmd_todo)
    
    # Test stubs command
    stubs_parser = subparsers.add_parser('stubs', help='Generate test stubs for untested code')
    stubs_parser.add_argument('--module', type=str, default=None,
                             help='Module to generate stubs for (all modules if None)')
    stubs_parser.add_argument('--repo-root', type=Path, default=None,
                             help='Repository root directory (auto-detected if None)')
    stubs_parser.set_defaults(func=cmd_stubs)
    
    # Test suite command
    suite_parser = subparsers.add_parser('suite', help='Generate a comprehensive test suite')
    suite_parser.add_argument('--repo-root', type=Path, default=None,
                             help='Repository root directory (auto-detected if None)')
    suite_parser.set_defaults(func=cmd_suite)
    
    # Run tests command
    run_parser = subparsers.add_parser('run', help='Run tests')
    run_parser.add_argument('--pattern', type=str, default='test_*.py',
                           help='Test file pattern to match')
    run_parser.add_argument('--verbose', '-v', action='store_true',
                           help='Show detailed output')
    run_parser.add_argument('--repo-root', type=Path, default=None,
                           help='Repository root directory (auto-detected if None)')
    run_parser.set_defaults(func=cmd_run)

def main() -> int:
    """
    Main entry point for the test command.
    
    Returns:
        Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(
        description="🌀 Eidosian Test Command System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    add_test_subparsers(subparsers)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        return args.func(args)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
