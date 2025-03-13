#!/usr/bin/env python3
# 🌀 Eidosian Inline Reference Fixer

import re
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
)
logger = logging.getLogger("eidosian_docs.inline_refs")

def fix_inline_references(docs_dir: Path = Path("../docs")) -> int:
    """Fix inline interpreted text reference issues in RST files."""
    fixed_files = 0
    
    # Focus on exceptions directory where most reference issues are
    exception_files = list(docs_dir.glob("**/exceptions/**/*.rst"))
    if not exception_files:
        # Fall back to searching all autoapi files
        exception_files = list(docs_dir.glob("**/autoapi/**/*.rst"))
    
    for rst_file in exception_files:
        try:
            with open(rst_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Find and fix unclosed inline references
            original_content = content
            
            # Fix `:class:X` without backticks to `:class:`X``
            content = re.sub(r'(:(?:class|exc|ref|meth|obj|mod):)([^`\s][^`\n]+?)(?=\s|\)|\n)', r'\1`\2`', content)
            
            # Fix any remaining unclosed backticks in docstrings
            content = re.sub(r'(`[^`\n]+?)(?=\n|\))', r'\1`', content)
            
            # Fix "Bases: :py:obj:`exception.Exception" pattern (missing closing backtick)
            content = re.sub(r'(Bases:.*?:py:[a-z]+:`[^`]+)(?!\`)', r'\1`', content)
            
            if content != original_content:
                with open(rst_file, "w", encoding="utf-8") as f:
                    f.write(content)
                fixed_files += 1
                logger.info(f"✅ Fixed inline references in {rst_file.name}")
        except Exception as e:
            logger.error(f"❌ Error processing {rst_file}: {e}")
    
    return fixed_files

if __name__ == "__main__":
    docs_dir = Path("../docs")
    if len(sys.argv) > 1:
        docs_dir = Path(sys.argv[1])
    
    fixed = fix_inline_references(docs_dir)
    print(f"Fixed inline references in {fixed} files")
