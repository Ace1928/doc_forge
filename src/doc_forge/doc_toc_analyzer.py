#!/usr/bin/env python3
# 🌀 Eidosian TOC Structure Analyzer
"""
TOC Structure Analyzer - Understanding Documentation Architecture

This script analyzes the Table of Contents structure in documentation to identify
structural issues, ensure proper hierarchy, and suggest improvements with
Eidosian precision and intelligence.

Following Eidosian principles of:
- Structure as Control: Perfect documentation organization
- Self-Awareness as Foundation: Understanding the document ecosystem
- Flow Like a River: Creating seamless navigation paths
- Contextual Integrity: Ensuring every document has purpose
"""

import os
import sys
import re
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, DefaultDict, Union
from collections import defaultdict, Counter

# 📊 Self-Aware Logging - Perfect understanding through observation
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("eidosian_docs.toc_analyzer")

class TocEntry:
    """Individual TOC entry with perfect structural awareness."""
    
    def __init__(self, title: str, target: str, level: int = 0, parent: Optional['TocEntry'] = None):
        self.title = title
        self.target = target
        self.level = level
        self.parent = parent
        self.children: List['TocEntry'] = []
        
    def add_child(self, child: 'TocEntry') -> None:
        """Add a child entry with perfect parent-child relationship."""
        child.parent = self
        self.children.append(child)
        
    def __repr__(self) -> str:
        """String representation with Eidosian clarity."""
        return f"TocEntry({self.title} -> {self.target}, level={self.level}, children={len(self.children)})"

class TocAnalyzer:
    """
    Table of Contents Analyzer with Eidosian intelligence.
    
    Analyzes documentation structure to ensure perfect organization,
    identify structural issues, and suggest improvements.
    """
    
    def __init__(self, docs_dir: Path):
        """
        Initialize the TOC analyzer with foundational knowledge.
        
        Args:
            docs_dir: Root directory of documentation
        """
        self.docs_dir = docs_dir
        self.docs_map: Dict[str, Path] = {}  # Maps doc IDs to paths
        self.entries_by_file: DefaultDict[str, List[TocEntry]] = defaultdict(list)
        self.main_toc: List[TocEntry] = []
        self.orphaned_docs: List[str] = []
        self.structural_issues: List[Dict[str, Any]] = []
        
        # Scan all documentation files
        self._scan_docs()
        # Extract TOC structures
        self._extract_toc_structures()
        
    def _scan_docs(self) -> None:
        """Build a map of all documentation files with zero friction."""
        # Process markdown files (primary format)
        for file_path in self.docs_dir.glob("**/*.md"):
            # Skip files in underscore directories (_build, _static, etc.)
            if any(p.startswith('_') for p in file_path.parts):
                continue
                
            # Get relative path for document ID
            rel_path = file_path.relative_to(self.docs_dir)
            doc_id = str(rel_path.with_suffix(''))  # Without extension
            doc_id_with_ext = str(rel_path)
            
            # Map both with and without extension for flexibility
            self.docs_map[doc_id] = file_path
            self.docs_map[doc_id_with_ext] = file_path
            
        # Process RST files (secondary format)
        for file_path in self.docs_dir.glob("**/*.rst"):
            if any(p.startswith('_') for p in file_path.parts):
                continue
                
            rel_path = file_path.relative_to(self.docs_dir)
            doc_id = str(rel_path.with_suffix(''))
            doc_id_with_ext = str(rel_path)
            
            self.docs_map[doc_id] = file_path
            self.docs_map[doc_id_with_ext] = file_path
            
        logger.debug(f"📚 Found {len(self.docs_map) // 2} documentation files")
    
    def _extract_toc_structures(self) -> None:
        """
        Extract TOC structures from all documentation files with perfect precision.
        """
        # Start with the main index file - the root of all structure
        index_path = self.docs_dir / "index.md"
        if not index_path.exists():
            index_path = self.docs_dir / "index.rst"
            
        if index_path.exists():
            self._extract_toc_from_file(index_path, is_main=True)
            
        # Then process all other files to find additional TOC structures
        for doc_id, file_path in self.docs_map.items():
            # Skip index files we already processed
            if file_path == index_path:
                continue
                
            # Only process actual files, not symbolic links or directories
            if file_path.is_file():
                self._extract_toc_from_file(file_path)
                
        # Identify orphaned documents after processing all TOCs
        self._identify_orphans()
        
        # Analyze structural issues
        self._analyze_structure()
                
    def _extract_toc_from_file(self, file_path: Path, is_main: bool = False) -> None:
        """
        Extract TOC entries from a single file.
        
        Args:
            file_path: Path to the documentation file
            is_main: Whether this is the main index file
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Extract toctree directives based on file format
            if file_path.suffix == '.md':
                toctree_blocks = re.findall(r'```{toctree}(.*?)```', content, re.DOTALL)
            elif file_path.suffix == '.rst':
                toctree_blocks = re.findall(r'\.\. toctree::(.*?)\n\n', content, re.DOTALL)
            else:
                return
            
            for block in toctree_blocks:
                # Extract caption if present
                caption_match = re.search(r':caption:\s*(.+)', block)
                caption = caption_match.group(1) if caption_match else ""
                
                # Extract maxdepth if present
                depth_match = re.search(r':maxdepth:\s*(\d+)', block)
                depth = int(depth_match.group(1)) if depth_match else 2
                
                # Extract entries - the core of TOC references
                entries = re.findall(r'\n\s*([a-zA-Z0-9_/.-]+)', block)
                
                rel_path = str(file_path.relative_to(self.docs_dir))
                for entry in entries:
                    entry = entry.strip()
                    if entry:
                        # Use basename as title if not explicitly provided
                        title = os.path.basename(entry).replace('_', ' ').title()
                        toc_entry = TocEntry(title, entry, 0)
                        self.entries_by_file[rel_path].append(toc_entry)
                        
                        if is_main:
                            self.main_toc.append(toc_entry)
                
        except Exception as e:
            logger.error(f"Error extracting TOC from {file_path}: {e}")
            
    def _parse_toc_block(self, block: str, file_path: Path, is_main: bool) -> None:
        """
        Parse a single TOC block and add entries to the TOC structure.
        
        Args:
            block: The TOC block content
            file_path: Path to the documentation file
            is_main: Whether this is the main index file
        """
        lines = block.strip().split('\n')
        current_entry: Optional[TocEntry] = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('..'):
                continue
            
            # Determine the level based on indentation
            level = (len(line) - len(line.lstrip())) // 4
            
            # Extract title and target
            if file_path.suffix == '.md':
                match = re.match(r'\[(.*?)\]\((.*?)\)', line)
                if match:
                    title, target = match.groups()
                else:
                    continue
            elif file_path.suffix == '.rst':
                title = line
                target = line.lower().replace(' ', '-')
            else:
                continue
            
            # Create a new TOC entry
            entry = TocEntry(title=title, target=target, level=level)
            
            if is_main and level == 0:
                self.main_toc.append(entry)
            elif current_entry and level > current_entry.level:
                current_entry.add_child(entry)
            else:
                self.entries_by_file[str(file_path)].append(entry)
                
            current_entry = entry
            
    def _identify_orphans(self) -> None:
        """Identify orphaned documents that are not part of any TOC."""
        all_docs = set(self.docs_map.keys())
        referenced_docs = set(entry.target for entries in self.entries_by_file.values() for entry in entries)
        self.orphaned_docs = list(all_docs - referenced_docs)
        
    def _analyze_structure(self) -> None:
        """Analyze the TOC structure and identify any issues."""
        for entries in self.entries_by_file.values():
            for entry in entries:
                if not entry.children and entry.target not in self.docs_map:
                    self.structural_issues.append({
                        "type": "missing_target",
                        "entry": entry
                    })
                    
        for doc_id in self.orphaned_docs:
            self.structural_issues.append({
                "type": "orphaned_document",
                "doc_id": doc_id
            })
            
    def report(self) -> None:
        """Generate a report of the TOC analysis."""
        print("TOC Analysis Report")
        print("===================")
        print("\nMain TOC:")
        for entry in self.main_toc:
            print(f"- {entry.title} ({entry.target})")
            
        print("\nOrphaned Documents:")
        for doc_id in self.orphaned_docs:
            print(f"- {doc_id}")
            
        print("\nStructural Issues:")
        for issue in self.structural_issues:
            print(f"- {issue['type']}: {issue.get('entry') or issue.get('doc_id')}")
            
def analyze_toc(docs_dir: Union[str, Path] = None, generate_report: bool = False) -> Dict[str, Any]:
    """
    Analyze TOC structure and identify issues with Eidosian precision.
    
    This function serves as the universal interface to the TOC analysis system,
    identifying structural issues in documentation organization.
    
    Args:
        docs_dir: Path to the documentation directory (auto-detected if None)
        generate_report: Whether to generate a detailed analysis report
        
    Returns:
        Dictionary with analysis results
    """
    # Auto-detect docs directory if not provided
    if docs_dir is None:
        # Try common locations
        possible_dirs = [
            Path("docs"),
            Path("../docs"),
            Path(__file__).resolve().parent.parent.parent / "docs"
        ]
        
        for path in possible_dirs:
            if path.is_dir():
                docs_dir = path
                break
                
        if docs_dir is None:
            logger.error("❌ Documentation directory not specified and couldn't be auto-detected")
            return {"error": "Documentation directory not found"}
    
    docs_dir = Path(docs_dir)
    
    if not docs_dir.is_dir():
        logger.error(f"❌ Not a valid directory: {docs_dir}")
        return {"error": f"Not a valid directory: {docs_dir}"}
    
    logger.info(f"🔍 Analyzing TOC structure in {docs_dir}")
    
    # Create analyzer and perform analysis
    analyzer = TocAnalyzer(docs_dir)
    
    # Prepare results
    results = {
        "main_toc_entries": len(analyzer.main_toc),
        "orphaned_documents": analyzer.orphaned_docs,
        "structural_issues": [issue["type"] for issue in analyzer.structural_issues],
        "issue_count": len(analyzer.structural_issues)
    }
    
    # Generate detailed report if requested
    if generate_report:
        results["detailed_report"] = {
            "toc_entries_by_file": {k: len(v) for k, v in analyzer.entries_by_file.items()},
            "main_toc_structure": [{"title": e.title, "target": e.target} for e in analyzer.main_toc],
            "issue_details": analyzer.structural_issues
        }
    
    logger.info(f"✅ TOC analysis complete. Found {results['issue_count']} issues")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze the TOC structure of documentation.")
    parser.add_argument("docs_dir", type=Path, help="Root directory of the documentation")
    args = parser.parse_args()
    
    analyzer = TocAnalyzer(args.docs_dir)
    analyzer.report()