#!/usr/bin/env python3
# 🌀 Eidosian TOC Tree Manager
"""
TOC Tree Manager - Optimizing Document Organization

This script ensures that documentation is properly organized in TOC trees without
duplications or orphaned documents. It analyzes the current state of the documentation
and adjusts TOC trees for optimal organization.

Following Eidosian principles of:
- Structure as Control: Perfect organization of documentation
- Contextual Integrity: Documents connected by logical relationships
- Self-Awareness: System that knows and improves its own structure
"""

import os
import re
import sys
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any

# 📊 Structured Logging - Self-Awareness Foundation
logging.basicConfig(level=logging.INFO,
                   format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")
logger = logging.getLogger("eidosian_docs.toctree_manager")

class TocTreeManager:
    """Manages and optimizes documentation TOC trees with architectural precision. 🏛️"""
    
    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir  # 📁 Documentation home
        self.index_file = docs_dir / "index.rst"  # 📄 Primary index
        if not self.index_file.exists() and (docs_dir / "index.md").exists():
            self.index_file = docs_dir / "index.md"  # 📝 Markdown alternative
        self.toctrees = {}  # 🌲 TOC tree registry
        self.referenced_docs = set()  # 🔗 Tracked references
        self.orphaned_docs = []  # 🏝️ Documents without a home
        self.duplicate_references = {}  # 🔄 Duplicated references
        
    def analyze_toctrees(self) -> None:
        """
        Analyze current TOC trees and identify issues.
        Like a detective examining the scene of disorganization! 🕵️‍♂️
        """
        if not self.index_file.exists():
            logger.warning(f"📛 Index file not found at {self.index_file}")
            return
            
        with open(self.index_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Find all toctree directives - the skeleton of our documentation
        toctree_matches = re.finditer(
            r'(?:\.\. toctree::|```{toctree})(.*?)(?:\n\n|\n[^\s])',
            content, re.DOTALL)
        
        for match in toctree_matches:
            toctree_content = match.group(1)
            toctree_docs = re.findall(r'\n\s+(\S+)', toctree_content)
            # Track references to find duplicates
            for doc in toctree_docs:
                if doc in self.referenced_docs:
                    if doc not in self.duplicate_references:
                        self.duplicate_references[doc] = []
                    self.duplicate_references[doc].append(match.start())
                    logger.debug(f"🔄 Found duplicate reference to {doc}")
                else:
                    self.referenced_docs.add(doc)
                    
        # Find all documents in the docs directory - the entire document universe
        all_docs = set()
        for root, _, files in os.walk(self.docs_dir):
            for file in files:
                if file.endswith(('.rst', '.md')) and not self._is_excluded(root, file):
                    rel_path = os.path.relpath(os.path.join(root, file), self.docs_dir)
                    rel_path = rel_path.replace('\\', '/') # Normalize paths
                    all_docs.add(rel_path)
                    
        # Strip extensions for comparison
        referenced_paths = {self._strip_extension(doc) for doc in self.referenced_docs}
        all_paths = {self._strip_extension(doc) for doc in all_docs}
        
        # Find orphans - the lonely documents
        self.orphaned_docs = list(all_paths - referenced_paths)
        logger.info(f"📊 Analysis complete: {len(self.referenced_docs)} referenced, {len(self.orphaned_docs)} orphaned docs")
        
    def _is_excluded(self, path: str, filename: str) -> bool:
        """Check if a file should be excluded from TOC processing."""
        exclude_dirs = ['_build', '_static', '_templates', '__pycache__']
        if any(excl in path for excl in exclude_dirs):
            return True
        excluded_files = ['conf.py', 'Thumbs.db', '.DS_Store']
        return filename in excluded_files
        
    def _strip_extension(self, path: str) -> str:
        """Strip file extensions for fair comparison."""
        return re.sub(r'\.(md|rst)$', '', path)
        
    def fix_toctrees(self) -> None:
        """
        Fix issues in TOC trees with surgical precision. 🔧
        Removes duplicates and ensures proper organization.
        """
        if not self.index_file.exists():
            logger.warning(f"📛 Index file not found at {self.index_file}")
            return
            
        with open(self.index_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Remove duplicate references - nobody likes seeing the same doc twice!
        modified = False
        for doc, positions in self.duplicate_references.items():
            if positions:
                logger.info(f"🔄 Removing duplicates of {doc}")
                modified = True
                # Keep first occurrence, remove others
                for pos in sorted(positions[1:], reverse=True):
                    content_before = content[:pos]
                    match_end = content.find('\n', pos + 1)
                    if match_end > 0:
                        content = content_before + content[match_end:]
                
        # Add orphaned documents to the main toctree
        if self.orphaned_docs:
            main_toctree_match = re.search(r'(?:\.\. toctree::|```{toctree})(.*?)(?:\n\n|\n[^\s])', content, re.DOTALL)
            if main_toctree_match:
                main_toctree_content = main_toctree_match.group(1)
                start_pos = main_toctree_match.start(1)
                end_pos = main_toctree_match.end(1)
                
                # Add each orphan if not already included
                additions = []
                for doc in self.orphaned_docs:
                    doc_path = doc if '.' in doc else f"{doc}"
                    if doc_path not in main_toctree_content:
                        additions.append(f"\n   {doc_path}")
                
                if additions:
                    logger.info(f"🏝️ Adding {len(additions)} orphaned docs to toctree")
                    updated_content = main_toctree_content + ''.join(additions)
                    content = content[:start_pos] + updated_content + content[end_pos:]
                    modified = True
                
        # Only write if changes were made - don't disturb what's already perfect
        if modified:
            with open(self.index_file, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"✅ TOC trees fixed in {self.index_file}")

    def add_orphan_directives(self) -> int:
        """
        Add :orphan: directive to truly orphaned documents that can't be in toctrees.
        Returns the count of documents fixed - a metric of achievement! 📊
        """
        fixed_count = 0
        for orphan in self.orphaned_docs:
            # Try both .rst and .md extensions
            rst_path = self.docs_dir / f"{orphan}.rst"
            md_path = self.docs_dir / f"{orphan}.md"
            
            file_path = None
            if rst_path.exists():
                file_path = rst_path
            elif md_path.exists():
                file_path = md_path
                
            if file_path and self._add_orphan_directive(file_path):
                fixed_count += 1
                
        return fixed_count
    
    def _add_orphan_directive(self, file_path: Path) -> bool:
        """Mark a document as orphaned to prevent build warnings."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Check if file already has orphan directive
            if ":orphan:" in content or "<!-- :orphan: -->" in content:
                return False
                
            # Add orphan directive at the top - every orphan deserves recognition
            if file_path.suffix == '.rst':
                new_content = f":orphan:\n\n{content}"
            else:  # Markdown
                new_content = f"<!-- :orphan: -->\n\n{content}"
                
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            logger.info(f"🏷️ Added orphan directive to {file_path.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}")
            return False
        
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("🔍 Usage: update_toctrees.py <docs_dir>")
        print("Example: update_toctrees.py /path/to/docs")
        sys.exit(1)
        
    docs_dir = Path(sys.argv[1])
    if not docs_dir.is_dir():
        logger.error(f"❌ Provided path is not a directory: {docs_dir}")
        sys.exit(1)
        
    print(f"🌲 TOCTree Manager initializing for {docs_dir}")
    manager = TocTreeManager(docs_dir)
    manager.analyze_toctrees()
    manager.fix_toctrees()
    orphan_count = manager.add_orphan_directives()
    print(f"✅ Fixed TOC trees and added {orphan_count} orphan directives")