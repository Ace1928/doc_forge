#!/usr/bin/env python3
# 🌀 Eidosian :noindex: Directive Optimizer
"""
Add :noindex: directives to duplicate objects in RST files
to prevent duplicate object descriptions during Sphinx build.

Following Eidosian principles of:
- Structure as Control: Each object needs a clear placement
- Flow Like a River: Documentation should flow without warnings
- Self-Awareness: System fixes its own redundancy issues
- Precision as Style: Surgical intervention with exact formatting
"""

import re
import logging
from pathlib import Path
from typing import Set, Dict, List, Tuple, Optional, Union, Any
import sys
import time
from functools import lru_cache

# 📊 Self-aware logging system - know thyself!
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
)
logger = logging.getLogger("eidosian_docs.noindex_fixer")

def add_noindex_to_duplicates(docs_dir: Path = Path(".")) -> int:
    """
    Add :noindex: directive to duplicate objects in RST files.
    
    Like a skilled diplomat ensuring each object knows its proper place! 🎭
    
    Args:
        docs_dir: Documentation directory to process
        
    Returns:
        int: Number of files fixed (victory count! 🏆)
    """
    start_time = time.time()  # ⏱️ Velocity as intelligence - measure performance
    
    # First step: take inventory of all objects - know your domain!
    rst_files = list(docs_dir.glob("**/*.rst"))
    fixed_count = 0
    seen_objects: Dict[str, Path] = {}  # Track first occurrence of each object
    duplicates: Dict[str, List[Path]] = {}  # Track duplicates for efficient processing
    
    logger.info(f"🔍 Scanning {len(rst_files)} RST files for duplicate objects...")
    
    # Analysis phase - map the territory before conquering it
    for rst_file in rst_files:
        try:
            with open(rst_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Extract object directives with precision - we need exact coordinates
            objects = re.finditer(
                r'(\.\. py:[a-z]+:: )([a-zA-Z0-9_.]+(?:\.[a-zA-Z0-9_]+)*)',
                content
            )
            
            for match in objects:
                object_name = match.group(2)
                
                # First sighting of this object? Record its homeland
                if object_name not in seen_objects:
                    seen_objects[object_name] = rst_file
                # Duplicate detected! Add to our diplomatic mission
                else:
                    if object_name not in duplicates:
                        duplicates[object_name] = []
                    duplicates[object_name].append(rst_file)
        except Exception as e:
            logger.warning(f"⚠️ File {rst_file.name} refused our diplomatic mission: {e}")
    
    # If no duplicates found, our work here is done - exhaustive but concise
    if not duplicates:
        duration = time.time() - start_time
        logger.info(f"🎉 No duplicate objects found - your docs are already unique! [{duration:.2f}s]")
        return 0
        
    logger.info(f"🔍 Found {len(duplicates)} objects with duplicates - diplomacy required")
    
    # Action phase - apply the fixes with surgical precision
    for object_name, duplicate_files in duplicates.items():
        for rst_file in duplicate_files:
            try:
                with open(rst_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Find all instances of this object in the file
                pattern = rf'(\.\. py:[a-z]+:: {re.escape(object_name)})\s*$'
                
                # Look for this exact object without :noindex: already present
                if ':noindex:' not in content[max(0, content.find(object_name)-50):min(len(content), content.find(object_name)+150)]:
                    updated_content = re.sub(
                        pattern,
                        r'\1\n   :noindex:',
                        content,
                        flags=re.MULTILINE
                    )
                    
                    # Only write if changed - don't waste energy (velocity as intelligence)
                    if updated_content != content:
                        with open(rst_file, "w", encoding="utf-8") as f:
                            f.write(updated_content)
                        logger.info(f"✅ Added :noindex: to {object_name} in {rst_file.name}")
                        fixed_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to fix {object_name} in {rst_file}: {e}")
    
    # Record final statistics - self-awareness as foundation
    duration = time.time() - start_time
    if fixed_count > 0:
        logger.info(f"🎯 Successfully added :noindex: directives to {fixed_count} files in {duration:.2f}s - duplicates tamed!")
    else:
        logger.info(f"👌 No changes needed - your documentation was already perfect! [{duration:.2f}s]")
    
    return fixed_count

@lru_cache(maxsize=16)
def get_warning_pattern():
    """Cached regex pattern for warning detection - velocity optimization."""
    return re.compile(r"WARNING:.*?duplicate object description of ['\"](.*?)['\"]")

def analyze_sphinx_warnings(build_log: Path) -> List[str]:
    """
    Extract duplicate object warnings from Sphinx build log.
    Like a detective finding clues in the warning logs! 🕵️‍♂️
    
    Args:
        build_log: Path to Sphinx build log file
        
    Returns:
        List of objects needing :noindex: directives
    """
    if not build_log.exists():
        logger.warning(f"⚠️ Build log not found at {build_log} - did you run Sphinx?")
        return []
    
    try:
        with open(build_log, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract duplicate warnings with precision - hyper-personal yet universal
        duplicate_warnings = get_warning_pattern().finditer(content)
        
        # Collect unique objects needing :noindex:
        objects_needing_noindex = set()
        for match in duplicate_warnings:
            objects_needing_noindex.add(match.group(1))
            
        if objects_needing_noindex:
            logger.info(f"🔍 Found {len(objects_needing_noindex)} objects with duplicate warnings")
            for obj in sorted(list(objects_needing_noindex))[:5]:  # Show first few
                logger.info(f"  • {obj}")
            if len(objects_needing_noindex) > 5:
                logger.info(f"    ... and {len(objects_needing_noindex) - 5} more")
        else:
            logger.info("✨ No duplicate object warnings found - your docs are pristine!")
            
        return list(objects_needing_noindex)
    
    except Exception as e:
        logger.error(f"❌ Error analyzing build log: {e}")
        return []

def targeted_fix_from_warnings(docs_dir: Path, warnings: List[str]) -> int:
    """
    Apply :noindex: directives specifically to objects from warning list.
    Like a surgical strike team, fixing only what needs fixing! 🎯
    
    Args:
        docs_dir: Documentation directory
        warnings: List of object names from warnings
        
    Returns:
        Number of files fixed
    """
    if not warnings:
        return 0
        
    fixed_count = 0
    rst_files = list(docs_dir.glob("**/*.rst"))
    
    # Show progress - flow like a river
    print(f"\n🔍 Searching {len(rst_files)} RST files for {len(warnings)} warned objects")
    print("   [", end="", flush=True)
    
    # Process each warned object - precision as style
    progress_step = max(1, len(warnings) // 20)
    for i, obj_name in enumerate(warnings):
        # Keep track of first occurrence - that one stays without :noindex:
        first_occurrence_found = False
        
        for rst_file in rst_files:
            try:
                with open(rst_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Skip if object isn't in this file - velocity as intelligence
                if obj_name not in content:
                    continue
                    
                # Check if this object is in the file
                escaped_name = re.escape(obj_name)
                pattern = rf'(\.\. py:[a-z]+:: {escaped_name})\s*$'
                match = re.search(pattern, content, re.MULTILINE)
                
                if match:
                    # First occurrence found - skip it
                    if not first_occurrence_found:
                        first_occurrence_found = True
                        continue
                    
                    # Check if :noindex: is already present
                    pos = match.start()
                    next_lines = content[pos:pos+200]
                    if ':noindex:' not in next_lines[:next_lines.find('\n\n') if '\n\n' in next_lines else len(next_lines)]:
                        # Add :noindex: to this duplicate
                        updated_content = re.sub(
                            pattern,
                            r'\1\n   :noindex:',
                            content,
                            flags=re.MULTILINE
                        )
                        
                        if updated_content != content:
                            with open(rst_file, "w", encoding="utf-8") as f:
                                f.write(updated_content)
                            fixed_count += 1
            except Exception as e:
                logger.warning(f"⚠️ Error processing {rst_file}: {e}")
                
        # Show progress - humor as cognitive leverage
        if i % progress_step == 0 or i == len(warnings) - 1:
            print("🔧", end="", flush=True)
            
    print("] Done!")
    return fixed_count

if __name__ == "__main__":
    # Show our beautiful ASCII banner - because style matters!
    print("""
╭────────────────────────────────────────────────────────╮
│      🔍  EIDOSIAN :noindex: DIRECTIVE OPTIMIZER  🔍    │
│     Bringing peace to duplicate objects since 2023     │
│   "Because documentation should be unique, like you!"  │
╰────────────────────────────────────────────────────────╯
    """)
    
    # Handle command line arguments with elegance
    docs_dir = Path(".")
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("\n🌟 Usage Options:")
            print("  python fix_no_index.py [docs_dir]")
            print("  python fix_no_index.py --analyze-log <log_file>")
            print("  python fix_no_index.py --fix-from-log <log_file> [docs_dir]")
            print("  python fix_no_index.py --help")
            print("\nExamples:")
            print("  python fix_no_index.py ../docs")
            print("  python fix_no_index.py --analyze-log ../docs/_build/output.log")
            sys.exit(0)
        elif sys.argv[1] == "--analyze-log" and len(sys.argv) > 2:
            # Analyze build log for warnings
            log_path = Path(sys.argv[2])
            analyze_sphinx_warnings(log_path)
            sys.exit(0)
        elif sys.argv[1] == "--fix-from-log" and len(sys.argv) > 2:
            # Fix based on warnings from log
            log_path = Path(sys.argv[2])
            docs_path = Path(".") 
            if len(sys.argv) > 3:
                docs_path = Path(sys.argv[3])
            warnings = analyze_sphinx_warnings(log_path)
            fixed = targeted_fix_from_warnings(docs_path, warnings)
            print(f"\n✅ Fixed {fixed} files based on warnings!")
            sys.exit(0)
        else:
            docs_dir = Path(sys.argv[1])
    
    # Run the main function with flair!
    logger.info(f"🚀 Starting :noindex: optimization for {docs_dir}")
    fixed_count = add_noindex_to_duplicates(docs_dir)
    logger.info(f"🎉 Mission accomplished! Fixed {fixed_count} files.")
    
    # Add a helpful tip - because we care about user experience
    if fixed_count > 0:
        print("\n💡 TIP: Run Sphinx build again to verify all duplicates are resolved!")
        print("       sphinx-build -b html docs docs/_build/html")
    else:
        print("\n💡 TIP: Your documentation is duplicate-free! Excellence achieved!")
        print("       Consider buying yourself a cookie. You deserve it! 🍪")
