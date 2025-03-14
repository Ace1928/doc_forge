#!/usr/bin/env python3
# 🌀 Eidosian Source Discovery System
"""
Source Discovery - Finding Documentation Sources with Eidosian Precision

This module discovers and catalogs documentation sources across the project,
ensuring all content is properly identified, categorized, and related.

Following Eidosian principles of:
- Contextual Integrity: Every document is precisely mapped
- Structure as Control: Perfect organization of documentation
- Exhaustive But Concise: Complete discovery without waste
"""

import os
import re
import logging
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Optional, Any

# Import project-wide information
from .global_info import get_doc_structure
from .utils.paths import get_repo_root, get_docs_dir

# 📊 Self-aware logging system
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
)
logger = logging.getLogger("doc_forge.source_discovery")

class DocumentMetadata:
    """Metadata for a discovered document with perfect structural awareness."""
    
    def __init__(self, path: Path, title: str = "", category: str = "", section: str = "", priority: int = 50):
        """
        Initialize document metadata.
        
        Args:
            path: Path to the document
            title: Document title
            category: Document category
            section: Document section
            priority: Document priority (0-100, lower is higher priority)
        """
        self.path = path
        self.title = title or path.stem.replace("_", " ").title()
        self.category = category
        self.section = section
        self.priority = priority
        self.url = str(path.with_suffix(".html")).replace("\\", "/")
        self.references: Set[str] = set()
        self.is_index = path.stem.lower() == "index"
        
        # Extract additional metadata from content
        self._extract_metadata()
    
    def _extract_metadata(self) -> None:
        """Extract metadata from document content with Eidosian precision."""
        if not self.path.exists():
            return
            
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Extract title
            if self.path.suffix == ".md":
                # Markdown title
                title_match = re.search(r'^#\s+(.*?)$', content, re.MULTILINE)
                if title_match:
                    self.title = title_match.group(1).strip()
            elif self.path.suffix == ".rst":
                # RST title
                title_match = re.search(r'^(.*?)\n[=]+\s*$', content, re.MULTILINE)
                if title_match:
                    self.title = title_match.group(1).strip()
            
            # Extract references to other documents
            if self.path.suffix == ".md":
                # Markdown links
                md_links = re.finditer(r'\[.*?\]\((.*?)\)', content)
                for match in md_links:
                    link = match.group(1).strip()
                    if not link.startswith(("http:", "https:", "#")):
                        self.references.add(link)
            elif self.path.suffix == ".rst":
                # RST links
                rst_links = re.finditer(r':doc:`(.*?)`', content)
                for match in rst_links:
                    link = match.group(1).strip()
                    self.references.add(link)
        except Exception as e:
            logger.warning(f"⚠️ Error extracting metadata from {self.path}: {e}")
    
    def __repr__(self) -> str:
        """String representation with Eidosian clarity."""
        return f"DocumentMetadata(title='{self.title}', path='{self.path}', category='{self.category}')"

class DocumentationDiscovery:
    """
    Documentation discovery system with Eidosian precision.
    
    Discovers, categorizes, and relates documentation across the project.
    """
    
    def __init__(self, repo_root: Optional[Path] = None, docs_dir: Optional[Path] = None):
        """
        Initialize the documentation discovery system.
        
        Args:
            repo_root: Repository root directory (auto-detected if None)
            docs_dir: Documentation directory (auto-detected if None)
        """
        self.repo_root = repo_root or get_repo_root()
        self.docs_dir = docs_dir or get_docs_dir()
        self.doc_structure = get_doc_structure(self.repo_root)
        
        # Track discovered documents - the map of all knowledge
        self.documents: Dict[str, List[DocumentMetadata]] = defaultdict(list)
        self.orphaned_documents: List[Path] = []
        self.tracked_documents: Set[str] = set()
    
    def discover_all(self) -> Dict[str, List[DocumentMetadata]]:
        """
        Discover all documentation files with Eidosian thoroughness.
        
        Returns:
            Dictionary mapping categories to lists of document metadata
        """
        self.documents.clear()
        self.orphaned_documents.clear()
        self.tracked_documents.clear()
        
        # Start with user documentation - hand-crafted wisdom
        self._discover_user_docs()
        
        # Then auto-generated documentation - machine precision
        self._discover_auto_docs()
        
        # Finally, AI-generated documentation - synthetic intelligence
        self._discover_ai_docs()
        
        # Identify orphaned documents - lost souls seeking purpose
        self._identify_orphans()
        
        return self.documents
    
    def _discover_user_docs(self) -> None:
        """Discover user documentation with perfect precision."""
        user_docs_dir = self.doc_structure.get("user_docs", self.docs_dir / "user_docs")
        
        if not user_docs_dir.exists():
            logger.warning(f"⚠️ User documentation directory not found at {user_docs_dir}")
            return
        
        # Process each section of user documentation
        for section in os.listdir(user_docs_dir):
            section_dir = user_docs_dir / section
            if not section_dir.is_dir():
                continue
                
            # Process all markdown and RST files in this section
            for ext in [".md", ".rst"]:
                for file_path in section_dir.glob(f"**/*{ext}"):
                    # Skip files in underscore directories
                    if any(p.startswith("_") for p in file_path.parts):
                        continue
                        
                    # Create document metadata
                    doc = DocumentMetadata(
                        path=file_path,
                        category="user",
                        section=section,
                        priority=30 if file_path.stem.lower() == "index" else 50
                    )
                    
                    self.documents["user"].append(doc)
                    
        logger.info(f"📚 Discovered {len(self.documents['user'])} user documentation files")
    
    def _discover_auto_docs(self) -> None:
        """Discover auto-generated documentation with systematic precision."""
        auto_docs_dir = self.doc_structure.get("auto_docs", self.docs_dir / "auto_docs")
        
        if not auto_docs_dir.exists():
            logger.warning(f"⚠️ Auto-generated documentation directory not found at {auto_docs_dir}")
            return
        
        # Check for common auto-doc directories
        autodoc_dirs = [
            auto_docs_dir / "api",
            auto_docs_dir / "introspected",
            auto_docs_dir / "extracted",
            self.docs_dir / "autoapi",  # Common AutoAPI output location
        ]
        
        for section_dir in autodoc_dirs:
            if not section_dir.exists():
                continue
                
            section = section_dir.name
            
            # Process all markdown and RST files in this section
            for ext in [".md", ".rst"]:
                for file_path in section_dir.glob(f"**/*{ext}"):
                    # Skip files in underscore directories
                    if any(p.startswith("_") for p in file_path.parts):
                        continue
                        
                    # Create document metadata
                    doc = DocumentMetadata(
                        path=file_path,
                        category="auto",
                        section=section,
                        priority=70  # Auto docs are typically lower priority in navigation
                    )
                    
                    self.documents["auto"].append(doc)
                    
        logger.info(f"🤖 Discovered {len(self.documents['auto'])} auto-generated documentation files")
    
    def _discover_ai_docs(self) -> None:
        """Discover AI-generated documentation with intelligent precision."""
        ai_docs_dir = self.doc_structure.get("ai_docs", self.docs_dir / "ai_docs")
        
        if not ai_docs_dir.exists():
            logger.debug(f"AI documentation directory not found at {ai_docs_dir}")
            return
        
        # Process each section of AI documentation
        for section in os.listdir(ai_docs_dir):
            section_dir = ai_docs_dir / section
            if not section_dir.is_dir():
                continue
                
            # Process all markdown and RST files in this section
            for ext in [".md", ".rst"]:
                for file_path in section_dir.glob(f"**/*{ext}"):
                    # Skip files in underscore directories
                    if any(p.startswith("_") for p in file_path.parts):
                        continue
                        
                    # Create document metadata
                    doc = DocumentMetadata(
                        path=file_path,
                        category="ai",
                        section=section,
                        priority=60  # AI docs are medium priority in navigation
                    )
                    
                    self.documents["ai"].append(doc)
                    
        logger.info(f"🧠 Discovered {len(self.documents['ai'])} AI-generated documentation files")
    
    def _identify_orphans(self) -> None:
        """
        Identify orphaned documentation files with compassionate precision.
        Orphaned files are those not properly placed in the structure.
        """
        # Find all markdown and RST files in docs directory
        all_docs = []
        for ext in [".md", ".rst"]:
            all_docs.extend(self.docs_dir.glob(f"**/*{ext}"))
        
        # Skip files in structure directories and underscore directories
        structure_dirs = {str(path) for path in self.doc_structure.values() if isinstance(path, Path)}
        
        for file_path in all_docs:
            # Skip files in underscore directories
            if any(p.startswith("_") for p in file_path.parts):
                continue
                
            # Check if this file is in a valid structure directory
            in_structure = False
            for dir_path in structure_dirs:
                if str(file_path).startswith(dir_path):
                    in_structure = True
                    break
            
            if not in_structure:
                self.orphaned_documents.append(file_path)
                
        logger.info(f"🏝️ Found {len(self.orphaned_documents)} orphaned documentation files")
    
    def generate_toc_structure(self, documents: Dict[str, List[DocumentMetadata]]) -> Dict:
        """
        Generate a table of contents structure based on discovered documents.
        
        Args:
            documents: Dictionary mapping categories to lists of document metadata
            
        Returns:
            Table of contents structure dictionary
        """
        # Initialize TOC structure
        toc = {
            "getting_started": {
                "title": "Getting Started",
                "items": []
            },
            "user_guide": {
                "title": "User Guide",
                "items": []
            },
            "concepts": {
                "title": "Concepts",
                "items": []
            },
            "reference": {
                "title": "API Reference",
                "items": []
            },
            "examples": {
                "title": "Examples",
                "items": []
            },
            "advanced": {
                "title": "Advanced Topics",
                "items": []
            }
        }
        
        # Map sections to TOC sections
        section_mapping = {
            "getting_started": "getting_started",
            "guides": "user_guide",
            "concepts": "concepts",
            "reference": "reference",
            "api": "reference",
            "examples": "examples",
            "advanced": "advanced",
            "faq": "user_guide",
        }
        
        # Process discovered documents and add to TOC
        for docs in documents.values():
            for doc in docs:
                # Determine target section
                target_section = section_mapping.get(doc.section, "reference")
                
                # Add to the appropriate section
                toc[target_section]["items"].append({
                    "title": doc.title,
                    "url": doc.url,
                    "priority": doc.priority
                })
                    
                # Mark this document as added
                self.tracked_documents.add(doc.url)
                
                # Process potential orphaned documents by removing them from our orphan list
                rel_url = doc.url.replace('.html', '')
                for orphan in self.orphaned_documents[:]:
                    orphan_url = str(orphan.relative_to(self.docs_dir)).replace('.md', '').replace('.rst', '')
                    if rel_url == orphan_url:
                        self.orphaned_documents.remove(orphan)
                        break
        
        # Try to intelligently place orphaned documents in appropriate sections
        if self.orphaned_documents:
            self._place_orphaned_documents(toc)
        
        # Sort items by priority within each section
        for section in toc.values():
            section["items"] = sorted(section["items"], key=lambda x: x.get("priority", 50))
            
        return toc
    
    def _place_orphaned_documents(self, toc: Dict) -> None:
        """
        Place orphaned documents into the appropriate toc sections based on their content.
        
        Args:
            toc: Table of contents structure to update
        """
        # Patterns to match document content with sections
        section_patterns = {
            "getting_started": ["installation", "quickstart", "setup", "introduction"],
            "user_guide": ["guide", "how to", "usage", "tutorial"],
            "concepts": ["concept", "architecture", "design", "principles"],
            "reference": ["api", "reference", "class", "function"],
            "examples": ["example", "sample", "demo"],
            "advanced": ["advanced", "expert", "internals", "deep dive"]
        }
        
        for orphan in self.orphaned_documents:
            # Skip if not a file or doesn't exist
            if not orphan.is_file() or not orphan.exists():
                continue
                
            # Create a default URL for the orphan
            orphan_url = str(orphan.relative_to(self.docs_dir)).replace('.md', '.html').replace('.rst', '.html')
            
            # Try to determine the best section based on filename and content
            best_section = None
            best_score = 0
            
            # Check filename first
            filename_lower = orphan.stem.lower()
            for section, patterns in section_patterns.items():
                for pattern in patterns:
                    if pattern in filename_lower:
                        if best_section is None:
                            best_section = section
                            best_score = 1
                        elif best_score < 2:  # Only override if we have a stronger match
                            best_section = section
                            best_score = 2
            
            # If no good match in filename, check content
            if best_score < 2:
                try:
                    with open(orphan, "r", encoding="utf-8") as f:
                        content = f.read().lower()
                        
                    for section, patterns in section_patterns.items():
                        section_score = sum(content.count(pattern) for pattern in patterns)
                        if section_score > best_score:
                            best_section = section
                            best_score = section_score
                except Exception:
                    pass  # If we can't read the file, use best guess so far
            
            # Default to reference if we couldn't determine a section
            if best_section is None:
                best_section = "reference"
                
            # Create a title from the filename if needed
            title = orphan.stem.replace("_", " ").title()
            
            # Try to extract a better title from the content
            try:
                with open(orphan, "r", encoding="utf-8") as f:
                    content_lines = f.readlines()
                    
                if orphan.suffix == ".md":
                    # Look for markdown title
                    for line in content_lines:
                        if line.startswith("# "):
                            title = line[2:].strip()
                            break
                elif orphan.suffix == ".rst":
                    # Look for RST title
                    for i, line in enumerate(content_lines):
                        if i > 0 and "===" in line and content_lines[i-1].strip():
                            title = content_lines[i-1].strip()
                            break
            except Exception:
                pass  # Use filename-based title if extraction fails
                
            # Add to the appropriate section
            toc[best_section]["items"].append({
                "title": title,
                "url": orphan_url,
                "priority": 90  # Orphaned docs get lowest priority
            })
            
            # Mark this document as tracked
            self.tracked_documents.add(orphan_url)
    
    def find_all_sources(self) -> Dict[str, List[Path]]:
        """
        Find all documentation sources across the project.
        
        Returns:
            Dictionary mapping categories to lists of file paths
        """
        all_sources = {
            "user": [],
            "auto": [],
            "ai": []
        }
        
        # Find user documentation
        user_docs_dir = self.doc_structure.get("user_docs", self.docs_dir / "user_docs")
        if user_docs_dir.exists():
            for ext in [".md", ".rst"]:
                all_sources["user"].extend(
                    [p for p in user_docs_dir.glob(f"**/*{ext}") 
                     if not any(part.startswith("_") for part in p.parts)]
                )
        
        # Find auto-generated documentation
        auto_docs_dir = self.doc_structure.get("auto_docs", self.docs_dir / "auto_docs")
        autoapi_dir = self.docs_dir / "autoapi"
        
        for directory in [auto_docs_dir, autoapi_dir]:
            if directory.exists():
                for ext in [".md", ".rst"]:
                    all_sources["auto"].extend(
                        [p for p in directory.glob(f"**/*{ext}") 
                        if not any(part.startswith("_") for part in p.parts)]
                    )
        
        # Find AI-generated documentation
        ai_docs_dir = self.doc_structure.get("ai_docs", self.docs_dir / "ai_docs")
        if ai_docs_dir.exists():
            for ext in [".md", ".rst"]:
                all_sources["ai"].extend(
                    [p for p in ai_docs_dir.glob(f"**/*{ext}") 
                     if not any(part.startswith("_") for part in p.parts)]
                )
        
        return all_sources
    
    def resolve_references(self) -> Dict[str, Set[str]]:
        """
        Resolve references between documentation files.
        
        Returns:
            Dictionary mapping document paths to sets of referenced documents
        """
        reference_map = {}
        
        # Process all discovered documents
        for docs in self.documents.values():
            for doc in docs:
                if doc.references:
                    reference_map[str(doc.path)] = doc.references
        
        return reference_map


def discover_documentation(docs_dir: Optional[Path] = None) -> Dict[str, List[DocumentMetadata]]:
    """
    Discover documentation files across the project with Eidosian precision.
    
    This function serves as the universal interface to the discovery system,
    finding all documentation files and their relationships.
    
    Args:
        docs_dir: Documentation directory (auto-detected if None)
        
    Returns:
        Dictionary mapping categories to lists of document metadata
    """
    # Auto-detect docs directory if not provided
    if docs_dir is None:
        docs_dir = get_docs_dir()
    
    logger.info(f"🔍 Discovering documentation in {docs_dir}")
    
    # Create discovery system and run discovery
    discovery = DocumentationDiscovery(docs_dir=docs_dir)
    documents = discovery.discover_all()
    
    logger.info(f"✅ Documentation discovery complete. Found {sum(len(docs) for docs in documents.values())} documents")
    return documents

def discover_code_structures(src_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Discover code structures in source code for documentation mapping.
    
    This function finds Python modules, classes and functions to map to documentation.
    
    Args:
        src_dir: Source directory to scan (auto-detected if None)
        
    Returns:
        List of discovered code entities with metadata
    """
    # Auto-detect source directory if not provided
    if src_dir is None:
        repo_root = get_repo_root()
        src_dir = repo_root / "src"
        if not src_dir.exists():
            # Try other common locations
            for candidate in [repo_root, repo_root / "lib", repo_root / "source"]:
                if candidate.exists() and any(p.suffix == ".py" for p in candidate.glob("**/*.py")):
                    src_dir = candidate
                    break
    
    if not src_dir.exists():
        logger.warning(f"⚠️ Source directory not found at {src_dir}")
        return []
    
    logger.info(f"🔍 Discovering code structures in {src_dir}")
    
    discovered_items = []
    
    # Find all Python files recursively
    python_files = list(src_dir.glob("**/*.py"))
    
    # Process each Python file
    for file_path in python_files:
        try:
            # Skip __init__.py files for simplicity
            if file_path.name == "__init__.py":
                continue
                
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Simple regex-based discovery (for demonstration)
            # In a production system, use the ast module for more accurate parsing
            
            # Find classes
            class_matches = re.finditer(r'class\s+([A-Za-z0-9_]+)(?:\(.*?\))?:', content)
            for match in class_matches:
                discovered_items.append({
                    "name": match.group(1),
                    "type": "class",
                    "file": str(file_path)
                })
                
            # Find functions
            func_matches = re.finditer(r'def\s+([A-Za-z0-9_]+)(?:\(.*?\))?:', content)
            for match in func_matches:
                func_name = match.group(1)
                # Skip private functions
                if func_name.startswith("_") and not (func_name.startswith("__") and func_name.endswith("__")):
                    continue
                    
                discovered_items.append({
                    "name": func_name,
                    "type": "function",
                    "file": str(file_path)
                })
                
        except Exception as e:
            logger.warning(f"⚠️ Error processing {file_path}: {e}")
    
    logger.info(f"✅ Code structure discovery complete. Found {len(discovered_items)} items")
    return discovered_items

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Discover documentation files.")
    parser.add_argument("docs_dir", nargs="?", type=Path, help="Documentation directory")
    parser.add_argument("--output", "-o", type=str, help="Output file for discovered documents")
    parser.add_argument("--format", "-f", choices=["json", "yaml", "text"], default="text",
                       help="Output format")
    args = parser.parse_args()
    
    discovered = discover_documentation(args.docs_dir)
    
    # Display summary
    print(f"📚 Documentation Discovery Report:")
    for category, docs in discovered.items():
        print(f"  {category.title()}: {len(docs)} documents")
    
    # Output detailed information if requested
    if args.output:
        if args.format == "json":
            import json
            with open(args.output, "w") as f:
                json.dump({cat: [{"title": doc.title, "path": str(doc.path)} for doc in docs]
                          for cat, docs in discovered.items()}, f, indent=2)
        elif args.format == "yaml":
            try:
                import yaml
                with open(args.output, "w") as f:
                    yaml.dump({cat: [{"title": doc.title, "path": str(doc.path)} for doc in docs]
                              for cat, docs in discovered.items()}, f)
            except ImportError:
                print("⚠️ PyYAML not installed. Using JSON format instead.")
                import json
                with open(args.output, "w") as f:
                    json.dump({cat: [{"title": doc.title, "path": str(doc.path)} for doc in docs]
                              for cat, docs in discovered.items()}, f, indent=2)
        else:
            with open(args.output, "w") as f:
                for category, docs in discovered.items():
                    f.write(f"=== {category.title()} ===\n")
                    for doc in docs:
                        f.write(f"{doc.title} ({doc.path})\n")
                    f.write("\n")
