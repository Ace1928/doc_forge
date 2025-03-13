#!/usr/bin/env python3
# 🌀 Eidosian Orphan Document Caretaker
"""
Ensure that standalone documentation files have the :orphan: directive
to prevent warnings about documents not being included in any toctree.

Following Eidosian principles of:
- Structure as Control: Every document needs a proper home
- Self-Awareness: Documentation system knows its own structure
- Contextual Integrity: Each document has appropriate directives
"""

import re
import sys
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any

# 📊 Self-aware logging - know thyself!
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
)
logger = logging.getLogger("eidosian_docs.orphan_fixer")

class TocTreeManager:
    """
    Manages and optimizes documentation TOC trees with architectural precision.
    Every document deserves a proper home! 🏡
    """
    
    def __init__(self, docs_dir: Path):
        """Initialize the TOC tree manager with a specific documentation directory."""
        self.docs_dir = docs_dir  # 📁 The realm we're managing
        self.index_file = docs_dir / "index.rst"  # 📄 The central directory
        if not self.index_file.exists() and (docs_dir / "index.md").exists():
            self.index_file = docs_dir / "index.md"  # 📝 Markdown alternative
        self.toctrees: Dict[str, List[str]] = {}  # 🌲 Registry of TOC trees
        self.referenced_docs: Set[str] = set()  # 🔗 Documents with a home
        self.orphaned_docs: List[str] = []  # 🏝️ Homeless documents
        self.doc_registry: Dict[str, Path] = {}  # 📚 Complete registry of all docs
        
    def analyze_toctrees(self) -> None:
        """
        Analyze current TOC trees and identify orphaned documents.
        Like a census taker mapping the documentation landscape! 🗺️
        """
        if not self.index_file.exists():
            logger.warning(f"📛 Index file not found at {self.index_file} - no central directory!")
            return
            
        # Read the index file - the master directory
        with open(self.index_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Find all toctree directives - the organizational structures
        toctree_matches = re.finditer(
            r'(?:\.\. toctree::|```{toctree})(.*?)(?:\n\n|\n[^\s])',
            content, re.DOTALL)
        
        # Extract all referenced documents from toctrees
        for match in toctree_matches:
            toctree_content = match.group(1)
            toctree_docs = re.findall(r'\n\s+(\S+)', toctree_content)
            
            # Track referenced documents
            for doc in toctree_docs:
                self.referenced_docs.add(doc)
                logger.debug(f"📎 Found reference to document: {doc}")
                    
        # Find all documents in the docs directory - the complete territory
        all_docs = set()
        for file_path in self.docs_dir.glob("**/*"):
            if file_path.is_file() and file_path.suffix in ('.rst', '.md'):
                # Skip files in special directories - they're not part of the documentation
                if any(excl in str(file_path) for excl in ["_build", "_static", "_templates", "__pycache__"]):
                    continue
                    
                rel_path = file_path.relative_to(self.docs_dir)
                rel_path_str = str(rel_path).replace('\\', '/')  # Normalize for cross-platform
                
                # Store the full file info in our registry
                self.doc_registry[rel_path_str] = file_path
                
                # Strip extension for comparison with references
                doc_id = rel_path_str.replace('.rst', '').replace('.md', '')
                all_docs.add(doc_id)
        
        # Find orphaned documents (those not referenced in any toctree)
        self.orphaned_docs = list(all_docs - self.referenced_docs)
        
        # Log the results - transparency builds trust!
        if self.orphaned_docs:
            logger.info(f"🏝️ Found {len(self.orphaned_docs)} orphaned documents out of {len(all_docs)} total")
            for orphan in self.orphaned_docs[:5]:  # Show first 5
                logger.debug(f"  • {orphan}")
            if len(self.orphaned_docs) > 5:
                logger.debug(f"  ... and {len(self.orphaned_docs) - 5} more")
        else:
            logger.info(f"✅ All {len(all_docs)} documents are properly referenced - perfect structure!")
        
    def add_orphan_directives(self) -> int:
        """
        Add :orphan: directive to orphaned documents to silence warnings.
        Giving each lonely document the care it deserves! 🤗
        
        Returns:
            Number of documents fixed
        """
        fixed_count = 0
        
        # Check if we've analyzed toctrees yet - if not, do it now
        if not hasattr(self, 'orphaned_docs') or self.orphaned_docs is None:
            self.analyze_toctrees()
        
        # Process each orphaned document
        for orphan in self.orphaned_docs:
            # Try both .rst and .md extensions
            rst_path = self.docs_dir / f"{orphan}.rst"
            md_path = self.docs_dir / f"{orphan}.md"
            
            # Use the path from registry if available (handles subdirectories better)
            for ext in ['.rst', '.md']:
                path_with_ext = f"{orphan}{ext}"
                if path_with_ext in self.doc_registry:
                    file_path = self.doc_registry[path_with_ext]
                    if self._add_orphan_to_file(file_path):
                        fixed_count += 1
                    break
            else:
                # Fallback to direct path checking
                if rst_path.exists():
                    if self._add_orphan_to_file(rst_path):
                        fixed_count += 1
                elif md_path.exists():
                    if self._add_orphan_to_file(md_path):
                        fixed_count += 1
        
        if fixed_count > 0:
            logger.info(f"✅ Added :orphan: directive to {fixed_count} documents - no more lonely docs!")
        else:
            logger.info("🔍 No orphaned documents needed fixing - already perfect!")
            
        return fixed_count
    
    def _add_orphan_to_file(self, file_path: Path) -> bool:
        """
        Add :orphan: directive to a specific file with elegance.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file was modified, False otherwise
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Check if file already has orphan directive - don't duplicate work
            if ":orphan:" in content or "<!-- :orphan: -->" in content:
                logger.debug(f"🔄 {file_path.name} already has orphan directive")
                return False
                
            # Format orphan directive based on file format - respect the file's language
            if file_path.suffix == '.rst':
                new_content = f":orphan:\n\n{content}"  # RST format
            else:  # Markdown
                new_content = f"<!-- :orphan: -->\n\n{content}"  # MD format
            
            # Write the updated content back to the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            logger.info(f"🏷️ Added orphan directive to {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}")
            return False
    
    def suggest_toctree_additions(self) -> Dict[str, List[str]]:
        """
        Suggest toctree additions for orphaned documents based on their content.
        Helping documents find their forever home! 🏠
        
        Returns:
            Dict mapping toctree names to lists of suggested document additions
        """
        if not self.orphaned_docs:
            return {}
            
        # Categories we might suggest
        suggestions = {
            "getting_started": [],
            "guides": [],
            "api": [],
            "examples": [],
            "reference": [],
            "misc": []
        }
        
        # Analyze each orphaned document
        for orphan in self.orphaned_docs:
            # Try to find the file
            file_path = None
            for ext in ['.rst', '.md']:
                path_with_ext = f"{orphan}{ext}"
                if path_with_ext in self.doc_registry:
                    file_path = self.doc_registry[path_with_ext]
                    break
            
            if not file_path or not file_path.exists():
                continue
                
            try:
                # Read the file content to analyze
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                
                # Categorize based on content and filename
                orphan_lower = orphan.lower()
                if any(kw in orphan_lower for kw in ["intro", "getting", "start", "install", "setup"]):
                    suggestions["getting_started"].append(orphan)
                elif any(kw in orphan_lower for kw in ["guide", "how", "tutorial"]):
                    suggestions["guides"].append(orphan)
                elif any(kw in orphan_lower for kw in ["api", "class", "interface", "method"]):
                    suggestions["api"].append(orphan)
                elif any(kw in orphan_lower for kw in ["example", "demo", "sample"]):
                    suggestions["examples"].append(orphan)
                elif any(kw in orphan_lower for kw in ["ref", "list", "spec", "details"]):
                    suggestions["reference"].append(orphan)
                else:
                    # Default category
                    suggestions["misc"].append(orphan)
            except Exception as e:
                logger.warning(f"⚠️ Error analyzing {file_path}: {e}")
                suggestions["misc"].append(orphan)
        
        # Remove empty categories
        return {k: v for k, v in suggestions.items() if v}

# 🚀 Main execution
if __name__ == "__main__":
    # Show our beautiful ASCII banner - because style matters!
    print("""
╭───────────────────────────────────────────╮
│ 🌀 EIDOSIAN ORPHAN DOCUMENT CARETAKER 🌀 │
│    Ensuring every document has a home!    │
╰───────────────────────────────────────────╯
    """)

    # Parse command line arguments
    if len(sys.argv) < 2:
        print("ℹ️ Usage: update_orphan_directives.py <docs_dir> [--suggest]")
        print("Example: update_orphan_directives.py /path/to/docs")
        sys.exit(1)
        
    # Get documentation directory
    docs_dir = Path(sys.argv[1])
    if not docs_dir.is_dir():
        logger.error(f"❌ Provided path is not a directory: {docs_dir}")
        sys.exit(1)
    
    # Create the manager
    manager = TocTreeManager(docs_dir)
    
    # Run the analysis
    logger.info(f"🔍 Analyzing documentation structure in {docs_dir}")
    manager.analyze_toctrees()
    
    # Fix orphaned docs
    fixed_count = manager.add_orphan_directives()
    
    # Suggest toctree additions if requested
    if "--suggest" in sys.argv:
        suggestions = manager.suggest_toctree_additions()
        
        if suggestions:
            print("\n📋 Suggested TOC Tree additions:")
            for category, docs in suggestions.items():
                print(f"\n🗂️ {category.upper()}:")
                for doc in docs:
                    print(f"  • {doc}")
        else:
            print("\n✅ No suggestions needed - all documents are well organized!")
    
    # Final status report
    if fixed_count > 0:
        print(f"\n✅ Added orphan directives to {fixed_count} documents")
    else:
        print("\n✅ No orphan directives needed - documentation structure is solid!")
