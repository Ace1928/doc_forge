#!/usr/bin/env python3
# 🌀 Eidosian Documentation Repair System
"""
Documentation Repair System - Comprehensive Eidosian Documentation Fix

This script runs all the documentation fixers in the correct order to address
common issues that might arise during documentation builds. It combines
docstring fixing, cross-reference resolution, and discovery of orphaned documents
to ensure perfect documentation.

Following Eidosian principles of:
- Self-Awareness as Foundation: System identifies and fixes its own weaknesses 
- Recursive Refinement: Each fix builds on previous improvements
- Flow Like a River: Seamless coordination between multiple fixing mechanisms
- Structure as Control: Organized approach to problem-solving
"""

import os
import sys
import logging
import importlib.util
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple
import time

# 🌊 Grace in imports - Flow Like a River principle
try:
    from .update_orphan_directives import TocTreeManager
except ImportError:
    try:
        from update_orphan_directives import TocTreeManager
    except ImportError:
        # Minimal fallback - Exhaustive but Concise principle
        class TocTreeManager:
            """Emergency TOC manager when real module unavailable. 🚑"""
            def __init__(self, docs_dir): self.docs_dir = docs_dir
            def analyze_toctrees(self): pass
            def add_orphan_directives(self): return 0
            def fix_toctrees(self): pass

# Graceful module import with fallback - Structure as Control
try:
    from fix_no_index import add_noindex_to_duplicates
except ImportError:
    def add_noindex_to_duplicates(docs_dir):
        """Stub function when module unavailable. 🏜️"""
        logging.warning("⚠️ fix_no_index module missing - duplicates may haunt your docs like ghosts")
        return 0

import subprocess

# 📊 Self-aware logging - Self-Awareness Foundation
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("eidosian_docs.repair")

def import_module_from_path(name: str, path: Path) -> Optional[Any]:
    """
    Import a module dynamically with precise error handling.
    Like finding a specific book in an infinite library! 📚
    
    Args:
        name: Module name to import
        path: Path to the module file
        
    Returns:
        Imported module or None if import failed
    """
    if not path.exists():
        return None
        
    try:
        spec = importlib.util.spec_from_file_location(name, str(path))
        if spec is None or spec.loader is None:
            return None
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"❌ Error importing {name}: {e}")
        return None

def run_fixers(repo_root: Path, skip_build: bool = False) -> None:
    """
    Run all documentation fixers in optimal sequence with surgical precision.
    A symphony of coordinated repairs! 🎭
    
    Args:
        repo_root: Repository root directory
        skip_build: If True, skip the Sphinx build step
    """
    docs_dir = repo_root / "docs"
    start_time = time.time()  # ⏱️ Track execution time - Velocity as Intelligence
    
    # 🌠 Step 1: Fix docstrings in source code - foundation first
    try:
        subprocess.run(["python", str(docs_dir / "fix_docstrings.py")], check=True)
        logger.info("📝 Fixed docstring formatting in source - clean roots, healthy tree!")
    except Exception as e:
        logger.error(f"❌ Docstring fixing crashed into the guardrails: {e}")
    
    # 🔄 Step 2: Add :noindex: directives - prevent duplication
    try:
        fixed = add_noindex_to_duplicates(docs_dir)
        logger.info(f"🔧 Added :noindex: to {fixed} files - duplicate objects now live in harmony")
    except Exception as e:
        logger.error(f"❌ :noindex: mission failed: {e}")
    
    # 📚 Step 3: Process orphaned documents - find lost children
    try:
        manager = TocTreeManager(docs_dir)
        manager.analyze_toctrees()
        count = manager.add_orphan_directives()
        logger.info(f"🏝️ Added orphan directives to {count} documents - every file needs a home")
    except Exception as e:
        logger.error(f"❌ Orphan document processing tripped: {e}")

    # 🧠 Step 4: Import fixer modules - assemble the repair team
    fixers: Dict[str, Any] = {}
    
    # Ordered for maximum flow - each building on the previous
    fix_priority = [
        "docstring_fixer",  # Start with readable code
        "autoapi_fixer",    # Then fix machine-generated docs
        "fix_cross_refs",   # Connect the knowledge graph
        "update_toctrees",  # Structure the navigation
        "source_discovery"  # Finally integrate everything
    ]
    
    for fixer_name in fix_priority:
        module_path = docs_dir / f"{fixer_name}.py"
        module = import_module_from_path(fixer_name, module_path)
        if module:
            fixers[fixer_name] = module
            logger.info(f"✅ Loaded {fixer_name} module - ready for action!")
        else:
            logger.warning(f"⚠️ Couldn't load {fixer_name}.py - this tool is MIA")
    
    # 📝 Step 5: Run docstring fixer - clarity first
    if "docstring_fixer" in fixers:
        try:
            fixer = fixers["docstring_fixer"].DocstringFixer(docs_dir)
            fixed = fixer.fix_all_files()
            logger.info(f"📝 Fixed docstrings in {fixed} files - clarity sparks joy!")
        except Exception as e:
            logger.error(f"❌ Docstring fixer stumbled: {e}")
    
    # 🤖 Step 6: Fix AutoAPI docs - clean up the machine's mess
    if "autoapi_fixer" in fixers:
        try:
            fixer = fixers["autoapi_fixer"].AutoAPIFixer(docs_dir)
            fixed = fixer.fix_all_files()
            logger.info(f"🔧 Fixed AutoAPI docs in {fixed} files - robots need guidance too")
        except Exception as e:
            logger.error(f"❌ AutoAPI fixer encountered a paradox: {e}")
    
    # 🔗 Step 7: Fix cross references - connect the dots
    if "fix_cross_refs" in fixers:
        try:
            fixers["fix_cross_refs"].fix_ambiguous_references(repo_root)
            fixers["fix_cross_refs"].fix_python_imports(repo_root)
            
            if hasattr(fixers["fix_cross_refs"], "create_intersphinx_mapping"):
                fixers["fix_cross_refs"].create_intersphinx_mapping(repo_root)
                
            logger.info("🔍 Fixed cross-references - no more broken links in the knowledge chain!")
        except Exception as e:
            logger.error(f"❌ Cross reference fixer lost its way: {e}")
    
    # 🌳 Step 8: Fix TOC trees - organize the forest
    if "update_toctrees" in fixers:
        try:
            # Fix different method name if necessary
            manager = fixers["update_toctrees"].TocTreeManager(docs_dir)
            manager.analyze_toctrees()
            
            # Try both method names for compatibility
            if hasattr(manager, "fix_toctree_issues"):
                manager.fix_toctree_issues()
            elif hasattr(manager, "fix_toctrees"):
                manager.fix_toctrees()
                
            count = manager.add_orphan_directives()
            logger.info(f"🌲 Fixed TOC trees and nestled {count} orphaned docs - structural harmony achieved")
        except Exception as e:
            logger.error(f"❌ TOC tree manager fell out of the tree: {e}")
    
    # 🔭 Step 9: Documentation discovery - map the territory
    if "source_discovery" in fixers:
        try:
            discovery = fixers["source_discovery"].DocumentationDiscovery(repo_root)
            documents = discovery.discover_all_documents()
            
            # Generate TOC - create the map
            toc = discovery.generate_toc_structure(documents)
            toctrees = discovery.generate_sphinx_toctree(toc)
            
            # Update index - the entry portal
            discovery.write_index_with_toctrees(toctrees)
            logger.info("📚 Updated index with discovered documents - the knowledge tree grows!")
            
            # Mark orphans - ensure every document is accounted for
            discovery.mark_orphaned_documents()
            logger.info(f"📌 Marked {len(discovery.orphaned_documents)} orphaned documents - no doc left behind")
        except Exception as e:
            logger.error(f"❌ Document discovery expedition failed: {e}")
    
    # 🏗️ Step 10: Run sphinx build - construct the final result
    if not skip_build:
        try:
            import re
            
            logger.info("🔄 Running Sphinx build - forging the documentation!")
            
            # First run with generous error tolerance
            process = subprocess.run(
                ["sphinx-build", "-b", "html", 
                 "-d", str(docs_dir / "_build/doctrees"), 
                 str(docs_dir), 
                 str(docs_dir / "_build/html")],
                capture_output=True,
                text=True
            )
            
            # Then try with strict warning enforcement
            if process.returncode == 0:
                logger.info("🎯 Initial build succeeded - now attempting perfectionist mode...")
                process_strict = subprocess.run(
                    ["sphinx-build", "-T", "-W", "--keep-going", "-b", "html", 
                     "-d", str(docs_dir / "_build/doctrees"), 
                     str(docs_dir), 
                     str(docs_dir / "_build/html")],
                    capture_output=True,
                    text=True
                )
                
                if process_strict.returncode == 0:
                    build_time = time.time() - start_time
                    logger.info(f"✨ Strict build passed flawlessly in {build_time:.2f}s! Documentation nirvana reached")
                else:
                    # Extract warnings
                    warnings = re.findall(r'WARNING:.*', process_strict.stderr)
                    errors = re.findall(r'ERROR:.*', process_strict.stderr)
                    
                    logger.warning(f"⚠️ Strict build completed with {len(warnings)} warnings and {len(errors)} errors")
                    if warnings:
                        logger.warning(f"First 5 warnings: {warnings[:5]}")
                    if errors:
                        logger.error(f"Errors: {errors}")
            else:
                logger.warning(f"⚠️ Initial build failed - the sphinx has spoken:\n{process.stderr[:500]}...")
                
        except Exception as e:
            logger.error(f"❌ Sphinx build crumbled: {e}")
            
    total_time = time.time() - start_time
    logger.info(f"⏱️ Documentation repair completed in {total_time:.2f}s - velocity is intelligence!")

if __name__ == "__main__":
    # Locate repository root with precision
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    
    # Parse arguments with clarity
    skip_build = "--skip-build" in sys.argv
    
    logger.info(f"🚀 Initiating Eidosian documentation repair - let's make these docs shine!")
    run_fixers(repo_root, skip_build)
    logger.info("✨ Documentation repair complete - knowledge flows freely once more")
    
    # Show help if needed - clear guidance
    if "--help" in sys.argv or len(sys.argv) == 1:
        print("\n📚 Usage: python fix_docs.py [options]")
        print("\nOptions:")
        print("  --skip-build    Skip the final Sphinx build step")
        print("  --help          Show this help message")
        print("\n🔮 Example: python fix_docs.py --skip-build")
