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
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
import logging
import re
import os
import sys
import json

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
            self.index_file = docs_dir / "index.md"
        self.manifest_path = docs_dir / "docs_manifest.json"  # 📘 Centralized manifest
        self.toctrees = {}  # 🌲 TOC tree registry
        self.referenced_docs = set()  # 🔗 Tracked references
        self.orphaned_docs = []  # 🏝️ Documents without a home
        self.duplicate_references = {}  # 🔄 Duplicated references
        self.manifest = self._load_manifest()  # 📊 Documentation manifest
        
    def _load_manifest(self) -> Dict:
        """Load the documentation manifest with precision and grace."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Failed to load manifest: {e}")
        return {}
        
    def analyze_toctrees(self) -> None:
        """
        Analyze current TOC trees and identify issues.
        Like a detective examining the scene of disorganization! 🕵️‍♂️
        """
        if not self.index_file.exists():
            logger.error(f"❌ Index file not found at {self.index_file}")
            return
            
        with open(self.index_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Find all toctree directives - the skeleton of our documentation
        toctree_matches = re.finditer(
            r'(?:\.\. toctree::|```{toctree})(.*?)(?:\n\n|\n[^\s])',
            content, re.DOTALL)
        
        for match in toctree_matches:
            toctree_content = match.group(1)
            toctree_lines = toctree_content.strip().split('\n')
            
            # Extract caption if present
            caption = None
            for line in toctree_lines:
                if ':caption:' in line:
                    caption = line.split(':caption:', 1)[1].strip()
                    break
            
            # Extract documents referenced in this toctree
            doc_matches = re.finditer(r'\n\s*([a-zA-Z0-9_/.-]+)', toctree_content)
            for doc_match in doc_matches:
                doc = doc_match.group(1).strip()
                self.referenced_docs.add(doc)
                
                # Track which toctree this document belongs to
                toc_key = caption or "main"
                if toc_key not in self.toctrees:
                    self.toctrees[toc_key] = []
                if doc not in self.toctrees[toc_key]:
                    self.toctrees[toc_key].append(doc)
                    
                # Check for duplicate references
                for other_toc_key, docs in self.toctrees.items():
                    if other_toc_key != toc_key and doc in docs:
                        if doc not in self.duplicate_references:
                            self.duplicate_references[doc] = []
                        self.duplicate_references[doc].append((toc_key, other_toc_key))
                    
        # Find all documents in the docs directory - the entire document universe
        all_docs = set()
        for root, _, files in os.walk(self.docs_dir):
            rel_path = Path(root).relative_to(self.docs_dir)
            for file in files:
                if file.endswith(('.md', '.rst')) and not self._is_excluded(root, file):
                    if rel_path == Path('.'):
                        all_docs.add(file)
                    else:
                        all_docs.add(str(rel_path / file))
                    
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
            logger.error(f"❌ Index file not found at {self.index_file}")
            return
            
        with open(self.index_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Remove duplicate references - nobody likes seeing the same doc twice!
        modified = False
        for doc, positions in self.duplicate_references.items():
            logger.info(f"🔄 Found duplicate reference to {doc} in toctrees: {positions}")
            # We keep the doc in the first toctree it appears in and remove from others
            for toc_key1, toc_key2 in positions:
                # Find the toctree with this caption and remove the duplicate doc
                toctree_pattern = rf'(:caption:\s*{re.escape(toc_key2)}.*?\n\s*)({re.escape(doc)})'
                if re.search(toctree_pattern, content, re.DOTALL):
                    content = re.sub(toctree_pattern, r'\1', content, flags=re.DOTALL)
                    modified = True
                    logger.info(f"✅ Removed duplicate reference to {doc} from toctree {toc_key2}")
                
        # Add orphaned documents to the main toctree
        if self.orphaned_docs:
            logger.info(f"🏝️ Adding {len(self.orphaned_docs)} orphaned documents to main toctree")
            # Find the last toctree directive
            toctree_match = list(re.finditer(r'(\.\. toctree::|```{toctree})(.*?)(?:\n\n|\n[^\s])', content, re.DOTALL))[-1]
            if toctree_match:
                toctree_end = toctree_match.end()
                # Add orphaned docs to the end of the last toctree
                orphan_entries = "\n".join(f"   {doc}" for doc in sorted(self.orphaned_docs))
                content = content[:toctree_end] + "\n" + orphan_entries + content[toctree_end:]
                modified = True
                
        # Only write if changes were made - don't disturb what's already perfect
        if modified:
            with open(self.index_file, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"✅ Updated TOC trees in {self.index_file}")

    def add_orphan_directives(self) -> int:
        """
        Add :orphan: directive to truly orphaned documents that shouldn't be in TOC.
        Returns the number of files modified.
        """
        count = 0
        for orphan in self.orphaned_docs:
            # Try both .md and .rst extensions
            for ext in [".md", ".rst"]:
                orphan_file = self.docs_dir / f"{orphan}{ext}"
                if orphan_file.exists() and self._add_orphan_directive(orphan_file):
                    count += 1
                    break
        return count
    
    def _add_orphan_directive(self, file_path: Path) -> bool:
        """Add :orphan: directive to a file if it doesn't already have one."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Check if file already has orphan directive
            if ":orphan:" in content:
                return False
                
            # Add orphan directive based on file type
            if file_path.suffix == ".md":
                new_content = f"<!-- :orphan: -->\n\n{content}"
            else:  # .rst
                new_content = f":orphan:\n\n{content}"
                
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            logger.info(f"✅ Added orphan directive to {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add orphan directive to {file_path}: {e}")
            return False

    def sync_with_manifest(self) -> None:
        """
        Synchronize TOC structure with the documentation manifest.
        The manifest becomes the single source of truth! 📖
        """
        if not self.manifest:
            logger.warning("⚠️ No manifest data available for synchronization")
            return
            
        try:
            # Update manifest with latest TOC analysis
            if "metadata" not in self.manifest:
                self.manifest["metadata"] = {}
                
            if "validation_status" not in self.manifest["metadata"]:
                self.manifest["metadata"]["validation_status"] = {}
                
            # Update orphaned docs list in manifest
            self.manifest["metadata"]["validation_status"]["orphaned_docs"] = self.orphaned_docs
            
            # Update document references
            doc_metrics = {
                "total_files": len(self.referenced_docs) + len(self.orphaned_docs),
                "referenced_files": len(self.referenced_docs),
                "orphaned_files": len(self.orphaned_docs),
                "duplicate_references": len(self.duplicate_references)
            }
            
            if "doc_metrics" not in self.manifest["metadata"]:
                self.manifest["metadata"]["doc_metrics"] = {}
                
            self.manifest["metadata"]["doc_metrics"].update(doc_metrics)
            
            # Save updated manifest
            with open(self.manifest_path, "w", encoding="utf-8") as f:
                json.dump(self.manifest, f, indent=4)
                
            logger.info(f"✅ Synchronized TOC analysis with manifest at {self.manifest_path}")
        except Exception as e:
            logger.error(f"❌ Failed to sync with manifest: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <docs_dir>")
        sys.exit(1)
        
    docs_dir = Path(sys.argv[1])
    if not docs_dir.is_dir():
        print(f"Error: {docs_dir} is not a directory")
        sys.exit(1)
        
    print(f"🌲 TOCTree Manager initializing for {docs_dir}")
    manager = TocTreeManager(docs_dir)
    manager.analyze_toctrees()
    manager.fix_toctrees()
    orphan_count = manager.add_orphan_directives()
    manager.sync_with_manifest()
    print(f"✅ Fixed TOC trees and added {orphan_count} orphan directives")