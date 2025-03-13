#!/usr/bin/env python3
# 🌀 Eidosian Documentation System - Universal Runner
"""
Universal Documentation Runner - The One Command Interface

This script integrates all documentation tools into a single, powerful CLI.
Built on pure Eidosian principles - structured, flowing, efficient, and aware.

Flow like water, strike like lightning.
"""

import os
import sys
import time
import argparse
import logging
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from datetime import datetime

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 Precision Logging - Self-aware from start to finish
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("doc_forge.runner")

# Replace path configuration with:
from .utils.paths import get_repo_root, get_docs_dir, resolve_path, ensure_dir

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛠️ Path Configuration - The foundation of structure
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Get essential paths using our dedicated path utilities
REPO_ROOT = get_repo_root()
DOCS_DIR = get_docs_dir()
BUILD_DIR = DOCS_DIR / "_build"
SCRIPTS_DIR = REPO_ROOT / "scripts"

# Debug log to ensure paths are correct
logger.debug(f"🔍 REPO_ROOT set to: {REPO_ROOT}")
logger.debug(f"🔍 DOCS_DIR set to: {DOCS_DIR}")
logger.debug(f"🔍 BUILD_DIR set to: {BUILD_DIR}")
logger.debug(f"🔍 SCRIPTS_DIR set to: {SCRIPTS_DIR}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚡ Command Execution - Zero friction operation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def run_command(
    command: Union[List[str], str], 
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    quiet: bool = False
) -> Tuple[int, str, str]:
    """
    Execute command with Eidosian precision and full awareness.
    
    Args:
        command: Command as list of arguments or string
        cwd: Working directory (defaults to REPO_ROOT)
        env: Environment variables to set
        quiet: Whether to suppress output logging
        
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    start_time = time.time()
    process_cwd = cwd or REPO_ROOT
    
    # Prepare environment
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    
    # Prepare shell mode based on command type
    shell = isinstance(command, str)
    cmd_str = command if shell else ' '.join(str(c) for c in command)
    
    if not quiet:
        logger.debug(f"Executing: {cmd_str}")
    
    try:
        process = subprocess.Popen(
            command,
            cwd=process_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=shell,
            env=process_env,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        
        # Track timing with precision
        execution_time = time.time() - start_time
        if not quiet:
            logger.debug(f"Command completed in {execution_time:.2f}s with code {process.returncode}")
        
        if process.returncode != 0 and not quiet:
            logger.warning(f"Command exited with code {process.returncode}")
            if stderr:
                logger.debug(f"stderr: {stderr[:200]}{'...' if len(stderr) > 200 else ''}")
        
        return process.returncode, stdout, stderr
        
    except Exception as e:
        if not quiet:
            logger.error(f"Command execution failed: {e}")
        return 1, "", str(e)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌊 Command Functions - Flow like water
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def cmd_all(args: argparse.Namespace) -> int:
    """
    Run the complete documentation workflow with one command.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success)
    """
    start = time.time()
    logger.info("🌀 Starting complete documentation workflow")
    
    # Step 1: Setup environment
    logger.info("🏗️ Setting up environment")
    code = cmd_setup(args)
    if code != 0:
        logger.error("❌ Setup failed")
        return code
    
    # Step 2: Fix issues
    logger.info("🔧 Fixing documentation issues")
    fix_args = argparse.Namespace()
    fix_args.fix_all = True
    code = cmd_fix(fix_args)
    if code != 0:
        logger.warning("⚠️ Some fixes failed, but continuing")
    
    # Step 3: Analyze structure
    logger.info("🔍 Analyzing documentation structure")
    analyze_args = argparse.Namespace()
    analyze_args.report = False
    cmd_analyze(analyze_args)
    
    # Step 4: Build documentation
    logger.info("📚 Building documentation")
    build_args = argparse.Namespace()
    build_args.formats = ["html"]
    build_args.fix = False  # Already fixed
    build_args.open = args.open
    code = cmd_build(build_args)
    if code != 0:
        logger.error("❌ Build failed")
        return code
    
    # Done!
    elapsed = time.time() - start
    logger.info(f"✨ Complete documentation workflow finished in {elapsed:.1f}s")
    
    return 0

def cmd_setup(args: argparse.Namespace) -> int:
    """
    Set up documentation environment with all prerequisites.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success)
    """
    logger.info("🏗️ Setting up documentation environment")
    
    # Install Python dependencies with path safety
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
    
    # Check if the script exists before trying to run it
    script_path = SCRIPTS_DIR / "create_missing_files.sh"
    if script_path.exists():
        code, out, err = run_command(["chmod", "+x", str(script_path)])
        if code == 0:
            code, out, err = run_command([str(script_path)])
            
        if code != 0:
            logger.warning(f"⚠️ Script execution failed: {err}")
            # Fall back to Python-based directory creation
            logger.info("📁 Falling back to Python-based directory creation")
            create_directory_structure()
    else:
        # If script doesn't exist, create the directories directly
        logger.info("📁 Using built-in directory creation (script not found)")
        create_directory_structure()
    
    # Create build directory
    BUILD_DIR.mkdir(exist_ok=True, parents=True)
    (BUILD_DIR / "html").mkdir(exist_ok=True)
    
    logger.info("✅ Documentation environment setup complete")
    return 0

def create_directory_structure() -> None:
    """
    Create the necessary directory structure for documentation.
    This is a fallback for when the shell script isn't available.
    """
    # Create all required directories
    dirs_to_create = [
        DOCS_DIR / "_build" / "html",
        DOCS_DIR / "_static" / "css",
        DOCS_DIR / "_static" / "js",
        DOCS_DIR / "_static" / "img",
        DOCS_DIR / "_templates",
        DOCS_DIR / "user_docs",
        DOCS_DIR / "auto_docs",
        DOCS_DIR / "api_docs",
        DOCS_DIR / "assets",
    ]
    
    for directory in dirs_to_create:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"📁 Created directory: {directory}")
    
    # Create minimal CSS file
    css_file = DOCS_DIR / "_static" / "css" / "custom.css"
    if not css_file.exists():
        with open(css_file, "w", encoding="utf-8") as f:
            f.write("""/* Custom CSS for documentation */
:root {
    --font-size-base: 16px;
    --line-height-base: 1.5;
}

.wy-nav-content {
    max-width: 900px;
}

.highlight {
    border-radius: 4px;
}

/* Dark mode support for code blocks */
@media (prefers-color-scheme: dark) {
    .highlight {
        background-color: #2d2d2d;
    }
}
""")
    
    # Create minimal JS file
    js_file = DOCS_DIR / "_static" / "js" / "custom.js"
    if not js_file.exists():
        with open(js_file, "w", encoding="utf-8") as f:
            f.write("""/* Custom JavaScript for documentation */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Doc Forge documentation loaded');
});
""")

    # Create placeholder READMEs
    for dir_name in ["user_docs", "auto_docs", "api_docs", "assets"]:
        readme_file = DOCS_DIR / dir_name / "README.md"
        if not readme_file.exists():
            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(f"# {dir_name.replace('_', ' ').title()}\n\n")
                f.write("This directory contains documentation files.\n")

def cmd_fix(args: argparse.Namespace) -> int:
    """
    Fix documentation issues with Eidosian precision.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success)
    """
    logger.info("🔧 Fixing documentation issues")
    
    # Update cross-references
    logger.info("🔗 Fixing cross-references")
    code, out, err = run_command([sys.executable, str(SCRIPTS_DIR / "update_cross_references.py"), str(DOCS_DIR)])
    if code != 0:
        logger.error(f"❌ Failed to fix cross-references: {err}")
        return code
        
    # Fix orphan documents with proper directives
    if hasattr(args, 'fix_orphans') and args.fix_orphans:
        logger.info("🏝️ Adding orphan directives to standalone files")
        code, out, err = run_command([sys.executable, str(SCRIPTS_DIR / "doc_toc_analyzer.py"), str(DOCS_DIR), "--fix"])
        if code != 0:
            logger.warning(f"⚠️ Adding orphan directives had issues: {err}")
    
    # Fix TOC structure issues
    if hasattr(args, 'fix_toc') and args.fix_toc:
        logger.info("🌳 Fixing TOC structure issues")
        code, out, err = run_command([sys.executable, str(SCRIPTS_DIR / "doc_toc_analyzer.py"), str(DOCS_DIR), "--auto-fix"])
        if code != 0:
            logger.warning(f"⚠️ TOC structure fixing had issues: {err}")
            
    logger.info("✅ Documentation fixes applied")
    return 0

def cmd_analyze(args: argparse.Namespace) -> int:
    """
    Analyze documentation structure and quality.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success)
    """
    logger.info("🔍 Analyzing documentation structure")
    
    # Use the TOC analyzer to scan structure
    report_args = ["--report"]
    if hasattr(args, 'json') and args.json:
        report_args.append("--json")
    if hasattr(args, 'output') and args.output:
        report_args.extend(["--output", args.output])
        
    cmd = [sys.executable, str(SCRIPTS_DIR / "doc_toc_analyzer.py"), str(DOCS_DIR)] + report_args
    code, out, err = run_command(cmd)
    
    if code != 0:
        logger.error(f"❌ Documentation analysis failed: {err}")
        return code
        
    logger.info("✅ Documentation analysis complete")
    return 0

def cmd_build(args: argparse.Namespace) -> int:
    """
    Build documentation with perfect Eidosian precision.
    
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
    ], quiet=True)
    
    if code != 0:
        logger.info("🔍 sphinx-autobuild not found, installing it")
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

def cmd_clean(args: argparse.Namespace) -> int:
    """
    Clean build artifacts with surgical precision.
    
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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐 Command Line Interface - The bridge between thought and action
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_parser() -> argparse.ArgumentParser:
    """Create command-line parser with Eidosian clarity."""
    parser = argparse.ArgumentParser(
        description="🌀 Doc Forge - Universal Documentation Command System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global options
    parser.add_argument(
        '--debug', action='store_true',
        help='Enable debug logging'
    )
    
    # Command subparsers
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # All-in-one command
    all_parser = subparsers.add_parser(
        'all', help='Run entire documentation workflow'
    )
    all_parser.add_argument(
        '--open', action='store_true',
        help='Open documentation after building'
    )
    
    # Setup command
    subparsers.add_parser(
        'setup', help='Set up documentation environment'
    )
    
    # Fix command
    fix_parser = subparsers.add_parser(
        'fix', help='Fix documentation issues'
    )
    fix_parser.add_argument(
        '--fix-all', action='store_true',
        help='Fix all issues'
    )
    fix_parser.add_argument(
        '--fix-orphans', action='store_true',
        help='Fix orphaned documents'
    )
    fix_parser.add_argument(
        '--fix-toc', action='store_true',
        help='Fix table of contents structure'
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze', help='Analyze documentation structure'
    )
    analyze_parser.add_argument(
        '--report', action='store_true',
        help='Generate analysis report'
    )
    analyze_parser.add_argument(
        '--json', action='store_true',
        help='Output report in JSON format'
    )
    analyze_parser.add_argument(
        '--output', type=str,
        help='Output file for report'
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
    
    # Serve command
    serve_parser = subparsers.add_parser(
        'serve', help='Serve documentation with live reload'
    )
    serve_parser.add_argument(
        '-p', '--port', type=int, default=8000,
        help='Port to serve on (default: 8000)'
    )
    
    # Clean command
    subparsers.add_parser(
        'clean', help='Clean build artifacts'
    )
    
    return parser

def main() -> int:
    """Main entry point for the command-line interface."""
    # Display Eidosian banner
    print(r"""
╔═══════════════════════════════════════════════════════════════════╗
║   ██████╗   █████╗   █████╗    ███████╗  █████╗  ██████╗   █████╗  ███████╗  ║
║   ██╔══██╗ ██╔══██╗ ██╔══██╗  ██╔════╝ ██╔══██╗ ██╔══██╗ ██╔══██╗ ██╔════╝  ║
║   ██║  ██║ ██║  ██║ ██║  ╚═╝  █████╗   ██║  ██║ ██████╔╝ ██║  ╚═╝ █████╗    ║
║   ██║  ██║ ██║  ██║ ██║  ██╗  ██╔══╝   ██║  ██║ ██╔══██╗ ██║  ██╗ ██╔══╝    ║
║   ██████╔╝ ╚█████╔╝ ╚█████╔╝  ██║      ╚█████╔╝ ██║  ██║ ╚█████╔╝ ███████╗  ║
║   ╚═════╝   ╚════╝   ╚════╝   ╚═╝       ╚════╝  ╚═╝  ╚═╝  ╚════╝  ╚══════╝  ║
╟───────────────────────────────────────────────────────────────────╢
║              Eidosian Documentation System                        ║
║         Structure • Flow • Precision • Self-Awareness             ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    parser = build_parser()
    args = parser.parse_args()
    
    # Enable debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Execute the requested command
    if args.command == 'all':
        return cmd_all(args)
    elif args.command == 'setup':
        return cmd_setup(args)
    elif args.command == 'fix':
        return cmd_fix(args)
    elif args.command == 'analyze':
        return cmd_analyze(args)
    elif args.command == 'build':
        return cmd_build(args)
    elif args.command == 'serve':
        return cmd_serve(args)
    elif args.command == 'clean':
        return cmd_clean(args)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
