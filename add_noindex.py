#!/usr/bin/env python3
# 🌀 Eidosian Duplicate Object Resolver
"""
Add :noindex: directives to duplicate object descriptions in RST files.

This script systematically resolves duplicate object warnings
by adding :noindex: directives to all instances except the first occurrence.
Pure Eidosian principles in action: minimal intervention, maximum impact.
"""

import re
import sys
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# 📊 Self-aware logging - precise and informative
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
)
logger = logging.getLogger("eidosian_docs.noindex_resolver")

def add_noindex_directives(docs_dir: Path = Path("../docs")) -> int:
    """
    Add :noindex: directives to duplicate object descriptions.
    
    Args:
        docs_dir: Documentation directory to process
        
    Returns:
        Number of files modified
    """
    start_time = __import__('time').time()
    logger.info(f"🔍 Scanning for duplicate objects in {docs_dir}")
    
    # Track all seen objects and their locations
    object_registry = defaultdict(list)
    autoapi_dir = docs_dir / "autoapi"
    api_dir = docs_dir / "api"
    
    # Define priorities for different directories - higher number = higher priority
    priorities = {
        str(api_dir): 100,   # Standard API docs get priority
        str(docs_dir / "api/ollama_forge"): 110,  # Explicit API docs get highest priority
        str(autoapi_dir): 50,  # Auto-generated docs get :noindex: added
        str(docs_dir / "autoapi/ollama_forge"): 40  # Explicit autoapi docs get lowest priority
    }
    
    # Stage 1: Build registry of all objects
    for directory in [autoapi_dir, api_dir]:
        if not directory.exists():
            continue
        
        dir_priority = priorities.get(str(directory), 75)
        
        for rst_file in directory.glob("**/*.rst"):
            try:
                with open(rst_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Determine priority based on file path
                file_priority = dir_priority
                for path, priority in priorities.items():
                    if str(path) in str(rst_file):
                        file_priority = priority
                        break
                
                # Find all object directives with enhanced patterns
                patterns = [
                    r'^\.\. py:([a-z]+):: ([a-zA-Z0-9_\.\(\)]+)',  # Standard directive
                    r'^\.\. py:([a-z]+):: ([a-zA-Z0-9_\.]+(?:\.[a-zA-Z0-9_]+)*)',  # Qualified names
                    r'^\.\. py:(?:method|function):: ([a-zA-Z0-9_\.]+)(?:\([^)]*\))',  # Methods with parameters
                    r'^\.\. auto([a-z]+):: ([a-zA-Z0-9_\.]+(?:\.[a-zA-Z0-9_]+)*)'  # Auto directives
                ]
                
                for pattern in patterns:
                    for match in re.finditer(pattern, content, re.MULTILINE):
                        if len(match.groups()) == 2:
                            obj_type = match.group(1)
                            obj_name = match.group(2)
                        else:
                            obj_type = "method"
                            obj_name = match.group(1)
                        
                        # Clean up object name by removing parameters
                        if '(' in obj_name:
                            obj_name = obj_name.split('(')[0]
                        
                        # Normalize object names for comparison
                        normalized_name = obj_name
                        if not obj_name.startswith('ollama_forge.') and 'ollama_forge' in str(rst_file):
                            # Check if this is a namespaced object that needs normalization
                            if '.' not in obj_name or obj_name.count('.') == 1:
                                # Determine the module from file path
                                path_parts = rst_file.parts
                                if 'ollama_forge' in path_parts:
                                    idx = path_parts.index('ollama_forge')
                                    if idx + 1 < len(path_parts) and path_parts[idx+1] not in ['api', 'autoapi']:
                                        module = path_parts[idx+1]
                                        if not normalized_name.startswith(f"{module}."):
                                            normalized_name = f"ollama_forge.{module}.{obj_name}"
                        
                        # Store complete directive to have exact match for replacement
                        object_registry[normalized_name].append((rst_file, match.group(0), file_priority))
            except Exception as e:
                logger.warning(f"⚠️ Error scanning {rst_file}: {e}")
    
    # Stage 2: Identify duplicate objects
    duplicates = {obj: locations for obj, locations in object_registry.items() if len(locations) > 1}
    logger.info(f"🔍 Found {len(duplicates)} objects with duplicates")
    
    # Stage 3: Add :noindex: to all duplicates (preserving highest priority occurrence)
    modified_files = set()
    for obj_name, locations in duplicates.items():
        # Sort by priority (descending) - highest priority first
        sorted_locations = sorted(locations, key=lambda x: x[2], reverse=True)
        
        # Skip first occurrence - it will be the primary definition
        for rst_file, directive, _ in sorted_locations[1:]:
            try:
                with open(rst_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check if :noindex: already exists for this directive
                directive_pos = content.find(directive)
                if directive_pos == -1:
                    continue
                    
                next_line_pos = content.find('\n', directive_pos + len(directive))
                if next_line_pos == -1:
                    next_line_pos = len(content)
                    
                snippet = content[directive_pos:next_line_pos]
                
                if ':noindex:' not in snippet:
                    # Add :noindex: to this duplicate
                    pattern = rf'({re.escape(directive)})\s*$'
                    replacement = f"\\1\n   :noindex:"
                    new_content = re.sub(pattern, replacement, content, count=1, flags=re.MULTILINE)
                    
                    if new_content != content:
                        with open(rst_file, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        
                        modified_files.add(rst_file)
                        logger.debug(f"✅ Added :noindex: to {obj_name} in {rst_file.name}")
            except Exception as e:
                logger.warning(f"⚠️ Error processing {rst_file}: {e}")
    
    # Fix specific inline reference issues in exception files
    exception_files = list((docs_dir / "autoapi" / "ollama_forge" / "exceptions").glob("**/*.rst"))
    if not exception_files:
        # Look in alternative locations
        exception_files = list(docs_dir.glob("**/exceptions/**/*.rst"))
    
    for rst_file in exception_files:
        try:
            with open(rst_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Fix inline references like :class:exception.Exception missing backticks
            updated_content = re.sub(r'(:(?:class|exc|meth|mod|obj):)([^`\s][^`\n]+)(?=\s|\n|\))', r'\1`\2`', content)
            
            # Fix unclosed backticks at end of lines
            updated_content = re.sub(r'(`[^`\n]+)(?=\n|\))', r'\1`', updated_content)
            
            # Fix Bases patterns specifically 
            updated_content = re.sub(r'(Bases:.*?:py:[a-z]+:`[^`]+)(?!\`)', r'\1`', updated_content)
            
            if updated_content != content:
                with open(rst_file, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                modified_files.add(rst_file)
                logger.debug(f"✅ Fixed inline references in {rst_file.name}")
        except Exception as e:
            logger.warning(f"⚠️ Error fixing references in {rst_file}: {e}")
    
    duration = __import__('time').time() - start_time
    logger.info(f"✅ Added :noindex: directives to objects in {len(modified_files)} files in {duration:.2f}s")
    return len(modified_files)

def fix_inline_literal_references(docs_dir: Path = Path("../docs")) -> int:
    """
    Fix unclosed backticks and other inline literal issues in RST files.
    
    Args:
        docs_dir: Documentation directory to process
        
    Returns:
        Number of files modified
    """
    logger.info(f"🔍 Scanning for unclosed backticks in {docs_dir}")
    
    autoapi_dir = docs_dir / "autoapi"
    if not autoapi_dir exists():
        logger.warning(f"⚠️ AutoAPI directory not found: {autoapi_dir}")
        return 0
    
    modified_files = 0
    for rst_file in autoapi_dir.glob("**/*.rst"):
        try:
            with open(rst_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Fix incomplete backticks in class links
            updated_content = re.sub(r'(:class:|:exc:|:meth:|:mod:|:obj:)`([^`]+)(?=[^`]*$)', r'\1`\2`', content)
            
            # Fix inline text references with incomplete backticks
            lines = updated_content.split('\n')
            for i in range(len(lines)):
                count = lines[i].count('`')
                if count % 2 == 1:
                    # Line has odd number of backticks - find the unclosed one
                    if lines[i].find('`') < lines[i].rfind('`'):
                        # More complicated case with multiple backticks
                        positions = [j for j in range(len(lines[i])) if lines[i][j] == '`']
                        if len(positions) % 2 == 1:
                            # Add closing backtick at a sensible position
                            last_pos = positions[-1]
                            if last_pos < len(lines[i]) - 1 and lines[i][last_pos+1:].strip():
                                lines[i] = lines[i][:last_pos+1] + '`' + lines[i][last_pos+1:]
                    else:
                        # Simple case - just add a closing backtick
                        lines[i] = lines[i] + '`'
                
                # Check and fix mixed indentation
                if lines[i].startswith('   ') and not lines[i].startswith('    ') and lines[i].strip():
                    lines[i] = '    ' + lines[i][3:]
            
            updated_content = '\n'.join(lines)
            
            # Fix fallback_context docstring issues specifically
            if "fallback_context" in updated_content and "with client.fallback_context" in updated_content:
                # Fix common pattern in this docstring
                updated_content = re.sub(r'(`[^`\n]+)(?=\n)', r'\1`', updated_content)
                updated_content = re.sub(r'(```python.*?with client\.fallback_context.*?)(?=```)(?!\n\s*```)', 
                                        r'\1\n        ```', updated_content, flags=re.DOTALL)
            
            if updated_content != content:
                with open(rst_file, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                modified_files += 1
                logger.debug(f"✅ Fixed inline literal issues in {rst_file.name}")
        except Exception as e:
            logger.warning(f"⚠️ Error processing {rst_file}: {e}")
    
    logger.info(f"✅ Fixed inline literal issues in {modified_files} files")
    return modified_files

if __name__ == "__main__":
    # Show our beautiful ASCII banner - because style matters!
    print("""
╭───────────────────────────────────────────────────╮
│       🌟 EIDOSIAN DUPLICATE OBJECT RESOLVER 🌟    │
│    Making :noindex: directives bring harmony      │
╰───────────────────────────────────────────────────╯
    """)
    
    docs_dir = Path("../docs")
    if len(sys.argv) > 1 and sys.argv[1] != "--help":
        docs_dir = Path(sys.argv[1])
    
    if "--help" in sys.argv:
        print("\n📘 Usage Options:")
        print("  python add_noindex.py [docs_dir] [options]")
        print("\nOptions:")
        print("  --fix-literals  Also fix inline literal reference issues")
        print("  --help          Show this help message")
    else:
        # Add :noindex: directives to duplicate objects
        fixed_count = add_noindex_directives(docs_dir)
        
        # Optionally fix inline literal issues
        if "--fix-literals" in sys.argv or True:  # Always run this by default now
            literal_fixes = fix_inline_literal_references(docs_dir)
            print(f"\n✅ Total files fixed: {fixed_count + literal_fixes}")
        else:
            print(f"\n✅ Total files fixed: {fixed_count}")
        
        if fixed_count > 0:
            print("\n💡 TIP: Run Sphinx build again to verify all duplicates are resolved!")
        else:
            print("\n💡 TIP: No duplicate objects found - your docs are already harmonious!")
