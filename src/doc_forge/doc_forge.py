#!/usr/bin/env python3
# 🌀 Eidosian Documentation Command Center
"""
Doc Forge - Universal Documentation Command System

A centralized command interface for documentation operations, embodying
Eidosian principles of structure, flow, precision, and self-awareness.
This script orchestrates all documentation processes with brutal efficiency
and elegant control.

Each command is a precision instrument, each workflow a masterpiece of clarity.
"""

import os
import sys
import time
import argparse
import logging
import subprocess
import shlex
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Set, Any, Callable

# Import path utilities for perfect path handling
from .utils.paths import get_repo_root, get_docs_dir, ensure_dir

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 Self-aware logging - Track everything with precision
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("doc_forge")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛠️ Core paths - The foundation of our structure
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Use path utilities for consistent path resolution
REPO_ROOT = get_repo_root()
DOCS_DIR = get_docs_dir()
BUILD_DIR = DOCS_DIR / "_build"
SCRIPTS_DIR = REPO_ROOT / "scripts"

# Add debug log to verify paths
logger.debug(f"🔍 REPO_ROOT set to: {REPO_ROOT}")
logger.debug(f"🔍 DOCS_DIR set to: {DOCS_DIR}")
logger.debug(f"🔍 BUILD_DIR set to: {BUILD_DIR}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎭 Command execution - Pristine function execution
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def run_command(command: Union[List[str], str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    """
    Execute a shell command with surgical precision and comprehensive output capture.
    
    Args:
        command: Command to execute (list or string)
        cwd: Working directory for command execution
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    start_time = time.time()
    process_cwd = cwd or REPO_ROOT
    
    # Convert string command to list if needed
    if isinstance(command, str):
        command = shlex.split(command)
    
    try:
        process = subprocess.Popen(
            command,
            cwd=process_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        
        # Track execution time for performance analysis
        execution_time = time.time() - start_time
        logger.debug(f"Command completed in {execution_time:.2f}s with code {process.returncode}")
        
        if process.returncode != 0:
            logger.warning(f"Command exited with non-zero code: {process.returncode}")
            if stderr:
                logger.debug(f"stderr: {stderr[:500]}...")
                
        return process.returncode, stdout, stderr
        
    except Exception as e:
        logger.error(f"Command execution failed: {command}, Error: {e}")
        return 1, "", str(e)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 Command implementations - Each a surgeon's precision tool
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def cmd_setup(args: argparse.Namespace) -> int:
    """
    Set up documentation environment with all prerequisites.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success)
    """
    logger.info("🏗️ Setting up documentation environment")
    
    # Install Python dependencies - use proper path resolution
    requirements_path = DOCS_DIR / "requirements.txt"
    
    if not requirements_path.exists():
        # Try alternative locations
        alt_paths = [
            REPO_ROOT / "requirements.txt",  # Root-level requirements
            REPO_ROOT / "requirements" / "docs.txt",  # Dedicated docs requirements
        ]
        
        for path in alt_paths:
            if path.exists():
                requirements_path = path
                logger.info(f"📄 Using requirements from: {requirements_path}")
                break
                
    if not requirements_path.exists():
        # Create minimal requirements.txt if none exists
        logger.warning("⚠️ No requirements file found. Creating minimal one.")
        ensure_dir(requirements_path.parent)
        with open(requirements_path, "w") as f:
            f.write("# Documentation dependencies\nsphinx>=4.0.0\nsphinx-rtd-theme>=1.0.0\n")
    
    logger.info("📦 Installing Python dependencies")
    code, out, err = run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)])
    if code != 0:
        logger.error(f"❌ Failed to install dependencies: {err}")
        return code
    
    # Create necessary directory structure
    logger.info("📂 Creating directory structure")
    code, out, err = run_command(["chmod", "+x", str(SCRIPTS_DIR / "create_missing_files.sh")])
    if code == 0:
        code, out, err = run_command([str(SCRIPTS_DIR / "create_missing_files.sh")])
        
    if code != 0:
        logger.error(f"❌ Failed to create directory structure: {err}")
        return code
    
    # Create build directory
    BUILD_DIR.mkdir(exist_ok=True, parents=True)
    (BUILD_DIR / "html").mkdir(exist_ok=True)
    
    logger.info("✅ Documentation environment setup complete")
    return 0

def cmd_build(args: argparse.Namespace) -> int:
    """
    Build documentation with perfect precision.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success)
    """
    formats = args.formats or ["html"]
    fix = args.fix
    open_after = args.open
    
    if fix:
        # Fix issues before building
        logger.info("🔧 Fixing documentation issues")
        
        # Fix cross-references
        logger.info("🔗 Fixing cross-references")
        code, out, err = run_command([sys.executable, str(SCRIPTS_DIR / "update_cross_references.py"), str(DOCS_DIR)])
        if code != 0:
            logger.warning(f"⚠️ Cross-reference fixing had issues: {err}")
            
        # Add orphan directives to standalone files
        logger.info("🏝️ Adding orphan directives to standalone files")
        code, out, err = run_command([sys.executable, str(SCRIPTS_DIR / "update_orphan_directives.py"), str(DOCS_DIR)])
        if code != 0:
            logger.warning(f"⚠️ Orphan directive addition had issues: {err}")
            
    # Build documentation for each requested format
    for output_format in formats:
        logger.info(f"📚 Building {output_format.upper()} documentation")
        
        build_dir = BUILD_DIR / output_format
        build_dir.mkdir(exist_ok=True, parents=True)
        
        cmd = [sys.executable, "-m", "sphinx"]
        
        # Add format-specific options
        if output_format == "html":
            cmd.extend(["-b", "html"])
        elif output_format == "pdf":
            cmd.extend(["-b", "latex"])
        elif output_format == "epub":
            cmd.extend(["-b", "epub"])
        else:
            logger.error(f"❌ Unknown output format: {output_format}")
            continue
            
        cmd.extend([str(DOCS_DIR), str(build_dir)])
        
        # Run the build command
        code, out, err = run_command(cmd)
        
        if code != 0:
            logger.error(f"❌ {output_format.upper()} build failed: {err}")
            return code
            
        logger.info(f"✅ {output_format.upper()} build completed successfully")
        
        # For PDF, we need to run the LaTeX build
        if output_format == "pdf":
            logger.info("📄 Running LaTeX build to generate PDF")
            code, out, err = run_command(["make", "-C", str(build_dir), "all-pdf"])
            
            if code != 0:
                logger.error(f"❌ PDF generation failed: {err}")
                return code
                
            logger.info("✅ PDF generation completed successfully")
    
    # Open documentation if requested
    if open_after:
        html_index = BUILD_DIR / "html" / "index.html"
        if html_index.exists():
            logger.info(f"🌐 Opening documentation: {html_index}")
            
            if sys.platform == "linux":
                run_command(["xdg-open", str(html_index)])
            elif sys.platform == "darwin":
                run_command(["open", str(html_index)])
            elif sys.platform == "win32":
                run_command(["start", str(html_index)], shell=True)
    
    logger.info(f"📚 Documentation build complete. Output in: {BUILD_DIR}")
    return 0

def cmd_clean(args: argparse.Namespace) -> int:
    """
    Clean build artifacts with precision and thoroughness.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success)
    """
    logger.info("🧹 Cleaning documentation build artifacts")
    
    try:
        # Remove build directory
        import shutil
        
        if BUILD_DIR.exists():
            logger.info(f"🗑️ Removing build directory: {BUILD_DIR}")
            shutil.rmtree(BUILD_DIR, ignore_errors=True)
            
        # Remove sphinx doctrees
        doctrees = DOCS_DIR / "_build" / "doctrees" 
        if doctrees.exists():
            logger.info(f"🗑️ Removing doctrees: {doctrees}")
            shutil.rmtree(doctrees, ignore_errors=True)
            
        # Remove __pycache__ directories
        for pycache in DOCS_DIR.glob("**/__pycache__"):
            if pycache.is_dir():
                logger.debug(f"🗑️ Removing __pycache__: {pycache}")
                shutil.rmtree(pycache, ignore_errors=True)
                
        logger.info("✅ Clean operation completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Clean operation failed: {e}")
        return 1

def cmd_check(args: argparse.Namespace) -> int:
    """
    Check documentation for issues with laser precision.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success)
    """
    logger.info("🔍 Checking documentation for issues")
    
    # Find all documentation files
    markdown_files = list(DOCS_DIR.glob("**/*.md"))
    rst_files = list(DOCS_DIR.glob("**/*.rst"))
    total_files = len(markdown_files) + len(rst_files)
    
    logger.info(f"📊 Found {total_files} documentation files ({len(markdown_files)} Markdown, {len(rst_files)} RST)")
    
    # Check for broken references
    logger.info("🔗 Checking for broken references")
    code, out, err = run_command([
        sys.executable, "-m", "sphinx.ext.intersphinx", 
        str(DOCS_DIR / "conf.py")
    ])
    
    if code != 0:
        logger.warning(f"⚠️ Intersphinx check had issues: {err}")
    
    # Run Sphinx linkcheck
    logger.info("🔍 Running link check")
    code, out, err = run_command([
        sys.executable, "-m", "sphinx", "-b", "linkcheck",
        str(DOCS_DIR), str(BUILD_DIR / "linkcheck")
    ])
    
    if "broken links found" in err:
        logger.warning("⚠️ Broken links detected")
        # Extract and display broken links
        for line in err.splitlines():
            if "broken" in line or "error" in line.lower():
                logger.warning(f"  {line}")
    
    # Run a test build with warnings as errors
    logger.info("⚠️ Running test build with warnings-as-errors")
    code, out, err = run_command([
        sys.executable, "-m", "sphinx", "-b", "html", "-W",
        str(DOCS_DIR), str(BUILD_DIR / "test")
    ])
    
    if code != 0:
        logger.error("❌ Test build failed - documentation has warnings that would be errors")
        # Extract and display warnings
        for line in err.splitlines():
            if "WARNING:" in line:
                logger.warning(f"  {line}")
        return code
    else:
        logger.info("✅ Test build passed - documentation has no critical warnings")
    
    logger.info("✅ Documentation check completed")
    return 0

def cmd_serve(args: argparse.Namespace) -> int:
    """
    Serve documentation with live reload for development.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success)
    """
    port = args.port
    
    # Check if sphinx-autobuild is available
    code, out, err = run_command([
        sys.executable, "-c", 
        "import sphinx_autobuild; print('sphinx-autobuild is available')"
    ])
    
    if code != 0:
        logger.error("❌ sphinx-autobuild is not available, trying to install it")
        code, out, err = run_command([
            sys.executable, "-m", "pip", "install", "sphinx-autobuild"
        ])
        
        if code != 0:
            logger.error(f"❌ Failed to install sphinx-autobuild: {err}")
            return code
    
    logger.info(f"🌐 Starting documentation server on port {port}")
    logger.info("📋 Press Ctrl+C to stop the server")
    
    # Run sphinx-autobuild
    cmd = [
        sys.executable, "-m", "sphinx_autobuild",
        str(DOCS_DIR), str(BUILD_DIR / "html"),
        "--port", str(port),
        "--open-browser"
    ]
    
    # This will run until the user presses Ctrl+C
    try:
        process = subprocess.Popen(cmd)
        process.wait()
        return 0
    except KeyboardInterrupt:
        logger.info("🛑 Documentation server stopped")
        return 0
    except Exception as e:
        logger.error(f"❌ Failed to start documentation server: {e}")
        return 1

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📚 CLI infrastructure - The interface between thought and action
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def create_parser() -> argparse.ArgumentParser:
    """Create the command-line parser with all commands and options."""
    parser = argparse.ArgumentParser(
        description="🌀 Doc Forge - Universal Documentation Command System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--debug', action='store_true',
        help='Enable debug logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Setup command
    setup_parser = subparsers.add_parser(
        'setup', help='Set up documentation environment'
    )
    
    # Build command
    build_parser = subparsers.add_parser(
        'build', help='Build documentation'
    )
    build_parser.add_argument(
        '-f', '--formats', nargs='+', choices=['html', 'pdf', 'epub'],
        help='Output formats to build (default: html)'
    )
    build_parser.add_argument(
        '--fix', action='store_true',
        help='Fix documentation issues before building'
    )
    build_parser.add_argument(
        '--open', action='store_true',
        help='Open documentation after building'
    )
    
    # Clean command
    clean_parser = subparsers.add_parser(
        'clean', help='Clean build artifacts'
    )
    
    # Check command
    check_parser = subparsers.add_parser(
        'check', help='Check documentation for issues'
    )
    
    # Serve command
    serve_parser = subparsers.add_parser(
        'serve', help='Serve documentation with live reload'
    )
    serve_parser.add_argument(
        '-p', '--port', type=int, default=8000,
        help='Port to serve on (default: 8000)'
    )
    
    return parser

def main() -> int:
    """Main entry point for the command-line interface."""
    # Create ASCII banner for maximum eidosian aesthetics
    print(r"""
╔═════════════════════════════════════════════════════════════════════════════════╗
║   ██████╗   █████╗   ██████╗    ███████╗  ██████╗  ██████╗   ██████╗  ███████╗  ║
║   ██╔══██╗ ██╔══██╗ ██╔════╝    ██╔════╝ ██╔═══██╗ ██╔══██╗ ██╔════╝  ██╔════╝  ║
║   ██║  ██║ ██║  ██║ ██║         █████╗   ██║   ██║ ██████╔╝ ██║  ███╗ ██████║   ║
║   ██║  ██║ ██║  ██║ ██║         ██╔══╝   ██║   ██║ ██╔══██╗ ██║   ██║ ██║       ║
║   ██████╔╝ ╚█████╔╝ ╚██████╗    ██║      ╚██████╔╝ ██║  ██║ ╚██████╔╝ ███████╗  ║
║   ╚═════╝   ╚════╝   ╚═════╝    ╚═╝       ╚═════╝  ╚═╝  ╚═╝  ╚═════╝  ╚══════╝  ║
╟─────────────────────────────────────────────────────────────────────────────────╢
║            Eidosian Documentation Command Center                                ║
╚═════════════════════════════════════════════════════════════════════════════════╝
""")
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Enable debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Execute the requested command
    if args.command == 'setup':
        return cmd_setup(args)
    elif args.command == 'build':
        return cmd_build(args)
    elif args.command == 'clean':
        return cmd_clean(args)
    elif args.command == 'check':
        return cmd_check(args)
    elif args.command == 'serve':
        return cmd_serve(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
