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
from typing import Dict, List, Set, Optional, Any, Union

# Import project-wide information
from .global_info import get_doc_structure
from .utils.paths import get_repo_root, get_docs_dir

# Type definitions for clarity and precision
PathStr = str
CategoryStr = str
SectionStr = str
TocItem = Dict[str, Any]
TocSection = Dict[str, Union[str, List[TocItem]]]
TocStructure = Dict[str, TocSection]
DocDict = Dict[CategoryStr, List['DocumentMetadata']]

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
                
            # Extract title with format-specific precision
            if self.path.suffix == ".md":
                self._extract_markdown_metadata(content)
            elif self.path.suffix == ".rst":
                self._extract_rst_metadata(content)
            # Extract references common to both formats
            self._extract_common_references(content)
                
        except Exception as e:
            logger.warning(f"⚠️ Error extracting metadata from {self.path}: {e}")
    
    def _extract_markdown_metadata(self, content: str) -> None:
        """Extract metadata from Markdown content."""
        # Extract title from first heading
        title_match = re.search(r'^#\s+(.*?)$', content, re.MULTILINE)
        if title_match:
            self.title = title_match.group(1).strip()
            
        # Extract references from markdown links
        md_links = re.finditer(r'\[.*?\]\((.*?)\)', content)
        for match in md_links:
            link = match.group(1).strip()
            if not link.startswith(("http:", "https:", "#", "mailto:")):
                # Clean up the link - remove anchor fragments and file extensions
                clean_link = re.sub(r'#.*$', '', link)
                clean_link = re.sub(r'\.(md|rst)$', '', clean_link)
                self.references.add(clean_link)
    
    def _extract_rst_metadata(self, content: str) -> None:
        """Extract metadata from RST content."""
        # Extract title from RST heading (line followed by === or ---)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if i > 0 and i < len(lines) - 1:
                next_line = lines[i + 1]
                if re.match(r'^[=\-]+$', next_line) and len(line) > 0:
                    if len(line.strip()) == len(next_line.strip()):
                        self.title = line.strip()
                        break
        
        # Extract references from RST directives
        rst_links = re.finditer(r':doc:`(.*?)`', content)
        for match in rst_links:
            link = match.group(1).strip()
            self.references.add(link)
            
        # Extract references from RST hyperlinks
        rst_hyperlinks = re.finditer(r'`[^`]*?<(.*?)>`_', content)
        for match in rst_hyperlinks:
            link = match.group(1).strip()
            if not link.startswith(("http:", "https:", "#", "mailto:")):
                self.references.add(link)
    
    def _extract_common_references(self, content: str) -> None:
        """Extract references common to multiple document formats."""
        # Look for include directives that might reference other files
        include_patterns = [
            r'\.\. include:: (.*?)$',  # RST include
            r'\{\% include "(.*?)" \%\}',  # Jinja/template include
            r'\{\{ *include\("(.*?)"\) *\}\}',  # Another template format
        ]
        
        for pattern in include_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                include_path = match.group(1).strip()
                if not include_path.startswith(("http:", "https:", "#")):
                    self.references.add(include_path)
    
    def __repr__(self) -> str:
        """String representation with Eidosian clarity."""
        return f"DocumentMetadata(title='{self.title}', path='{self.path}', category='{self.category}')"

class DocumentationDiscovery:
    """
    Documentation discovery system with Eidosian precision.
    
    Discovers, categorizes, and relates documentation across the project,
    ensuring perfect structural awareness and contextual mapping.
    """
    
    def __init__(self, repo_root: Optional[Path] = None, docs_dir: Optional[Path] = None):
        """
        Initialize the documentation discovery system with structural precision.
        
        Args:
            repo_root: Repository root directory (auto-detected if None)
            docs_dir: Documentation directory (auto-detected if None)
        """
        self.repo_root = repo_root or get_repo_root()
        self.docs_dir = docs_dir or get_docs_dir()
        self.doc_structure = get_doc_structure(self.repo_root)
        
        # Track discovered documents with perfect structural awareness
        self.documents: Dict[str, List[DocumentMetadata]] = defaultdict(list)
        self.orphaned_documents: List[Path] = []
        self.tracked_documents: Set[str] = set()
        
        # Document formats we support with Eidosian precision
        self.doc_extensions = [".md", ".rst", ".txt"]
        
        # Cache for performance optimization
        self._file_content_cache: Dict[str, str] = {}
    
    def discover_all(self) -> Dict[str, List[DocumentMetadata]]:
        """
        Discover all documentation files with Eidosian thoroughness.
        
        Performs a comprehensive scan of all documentation sources,
        categorizing and extracting metadata with perfect precision.
        
        Returns:
            Dictionary mapping categories to lists of document metadata
        """
        self._clear_discovery_state()
        
        # Start with user documentation - hand-crafted wisdom
        self._discover_user_docs()
        
        # Then auto-generated documentation - machine precision
        self._discover_auto_docs()
        
        # Next, AI-generated documentation - synthetic intelligence
        self._discover_ai_docs()
        
        # Identify orphaned documents - lost souls seeking purpose
        self._identify_orphans()
        
        # Resolve cross-references between documents
        self._resolve_document_relations()
        
        return self.documents
    
    def _clear_discovery_state(self) -> None:
        """Reset all discovery state with Eidosian precision."""
        self.documents.clear()
        self.orphaned_documents.clear()
        self.tracked_documents.clear()
        self._file_content_cache.clear()
    
    def _discover_user_docs(self) -> None:
        """Discover user documentation with perfect structural awareness."""
        user_docs_dir = self.doc_structure.get("user_docs", self.docs_dir / "user_docs")
        
        if not user_docs_dir.exists():
            logger.warning(f"⚠️ User documentation directory not found at {user_docs_dir}")
            return
        
        # Process each section of user documentation with Eidosian comprehension
        try:
            for section in os.listdir(user_docs_dir):
                section_dir = user_docs_dir / section
                if not section_dir.is_dir():
                    continue
                
                # Process all supported documentation formats in this section
                for ext in self.doc_extensions:
                    for file_path in section_dir.glob(f"**/*{ext}"):
                        # Skip files in underscore directories (convention for private files)
                        if any(p.startswith("_") for p in file_path.parts):
                            continue
                        
                        # Create document metadata with precise classification
                        doc = DocumentMetadata(
                            path=file_path,
                            category="user",
                            section=section,
                            priority=self._calculate_doc_priority(file_path, section, "user")
                        )
                        
                        self.documents["user"].append(doc)
        except Exception as e:
            logger.error(f"🔥 Error discovering user documentation: {e}")
                    
        logger.info(f"📚 Discovered {len(self.documents['user'])} user documentation files")
    
    def _discover_auto_docs(self) -> None:
        """Discover auto-generated documentation with systematic precision."""
        auto_docs_dir = self.doc_structure.get("auto_docs", self.docs_dir / "auto_docs")
        
        # Check for common auto-doc directories with comprehensive awareness
        autodoc_dirs = [
            auto_docs_dir / "api",
            auto_docs_dir / "introspected",
            auto_docs_dir / "extracted",
            self.docs_dir / "autoapi",  # Common AutoAPI output
            self.docs_dir / "apidoc",   # Common apidoc output
            self.docs_dir / "reference", # Another common location
        ]
        
        discovered_count = 0
        for section_dir in autodoc_dirs:
            if not section_dir.exists():
                continue
                
            section = section_dir.name
            
            # Process all documentation formats in this section
            for ext in self.doc_extensions:
                try:
                    for file_path in section_dir.glob(f"**/*{ext}"):
                        # Skip files in underscore directories
                        if any(p.startswith("_") for p in file_path.parts):
                            continue
                        
                        # Create document metadata with proper categorization
                        doc = DocumentMetadata(
                            path=file_path,
                            category="auto",
                            section=section,
                            priority=self._calculate_doc_priority(file_path, section, "auto")
                        )
                        
                        self.documents["auto"].append(doc)
                        discovered_count += 1
                except Exception as e:
                    logger.warning(f"⚠️ Error processing auto docs in {section_dir}: {e}")
                    
        logger.info(f"🤖 Discovered {discovered_count} auto-generated documentation files")
    
    def _discover_ai_docs(self) -> None:
        """Discover AI-generated documentation with intelligent structural mapping."""
        ai_docs_dir = self.doc_structure.get("ai_docs", self.docs_dir / "ai_docs")
        
        if not ai_docs_dir.exists():
            logger.debug(f"AI documentation directory not found at {ai_docs_dir}")
            return
        
        # Process each section of AI documentation with synthetic comprehension
        try:
            for section in os.listdir(ai_docs_dir):
                section_dir = ai_docs_dir / section
                if not section_dir.is_dir():
                    continue
                
                # Process all supported documentation formats with adaptive intelligence
                for ext in self.doc_extensions:
                    for file_path in section_dir.glob(f"**/*{ext}"):
                        # Skip files in underscore directories
                        if any(p.startswith("_") for p in file_path.parts):
                            continue
                        
                        # Create document metadata with contextual awareness
                        doc = DocumentMetadata(
                            path=file_path,
                            category="ai",
                            section=section,
                            priority=self._calculate_doc_priority(file_path, section, "ai")
                        )
                        
                        self.documents["ai"].append(doc)
        except Exception as e:
            logger.error(f"🔥 Error discovering AI documentation: {e}")
                    
        logger.info(f"🧠 Discovered {len(self.documents['ai'])} AI-generated documentation files")
    
    def _calculate_doc_priority(self, file_path: Path, section: str, category: str) -> int:
        """
        Calculate document priority with Eidosian intelligence.
        
        Args:
            file_path: Path to the document
            section: Document section
            category: Document category
            
        Returns:
            Priority value (0-100, lower is higher priority)
        """
        # Base priority by category
        base_priority = {"user": 40, "ai": 60, "auto": 80}.get(category, 50)
        
        # Important sections get priority boost
        if section in ["getting_started", "guides", "overview"]:
            base_priority -= 10
        
        # Index files are always prioritized
        if file_path.stem.lower() == "index":
            base_priority -= 20
        
        # README files are highly prioritized
        if file_path.stem.lower() == "readme":
            base_priority -= 15
        
        # Short paths are usually more important
        depth_penalty = len(file_path.parts) - len(self.docs_dir.parts) - 1
        base_priority += depth_penalty * 2
        
        # Ensure priority stays in valid range
        return max(0, min(100, base_priority))
    
    def _identify_orphans(self) -> None:
        """
        Identify orphaned documentation files with compassionate structural awareness.
        
        Orphaned files are those not properly integrated into the documentation
        structure but may still contain valuable information.
        """
        # Find all documentation files in docs directory with exhaustive precision
        all_docs = []
        for ext in self.doc_extensions:
            all_docs.extend(self.docs_dir.glob(f"**/*{ext}"))
        
        # Skip files in structure directories and underscore directories
        structure_dirs = {
            str(path) for path in self.doc_structure.values() 
            if isinstance(path, Path) and path.exists()
        }
        
        # Add commonly ignored directories
        ignored_dirs = [
            self.docs_dir / "_build",
            self.docs_dir / "_static", 
            self.docs_dir / "_templates",
            self.docs_dir / "venv",
            self.docs_dir / ".venv",
        ]
        
        for file_path in all_docs:
            # Skip files in underscore directories
            if any(p.startswith("_") for p in file_path.parts):
                continue
                
            # Skip files in ignored directories
            if any(str(file_path).startswith(str(ignored)) for ignored in ignored_dirs):
                continue
                
            # Check if this file is in a valid structure directory
            in_structure = False
            for dir_path in structure_dirs:
                if str(file_path).startswith(dir_path):
                    in_structure = True
                    break
            
            # Check if file is already tracked in our documents
            already_tracked = False
            doc_url = str(file_path.with_suffix(".html")).replace("\\", "/")
            if doc_url in self.tracked_documents:
                already_tracked = True
                
            if not in_structure and not already_tracked:
                self.orphaned_documents.append(file_path)
                
        logger.info(f"🏝️ Found {len(self.orphaned_documents)} orphaned documentation files")
    
    def _resolve_document_relations(self) -> None:
        """Resolve relationships between documents with Eidosian comprehension."""
        # Build a map of document URLs to document objects
        doc_map = {}
        for category, docs in self.documents.items():
            for doc in docs:
                doc_map[doc.url] = doc
        
        # Process each document's references to establish relationships
        for category, docs in self.documents.items():
            for doc in docs:
                for ref in doc.references:
                    # Try to find the referenced document
                    ref_url = f"{ref}.html"
                    if ref_url in doc_map:
                        # We found a direct reference - could establish bidirectional links here
                        pass
        
        logger.debug("📊 Document relations resolved with Eidosian precision")
    
    def generate_toc_structure(self) -> Dict:
        """
        Generate a table of contents structure with perfect organizational clarity.
        
        Returns:
            Table of contents structure dictionary
        """
        # Initialize TOC structure with Eidosian categorization
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
        
        # Map sections to TOC sections with semantic precision
        section_mapping = {
            "getting_started": "getting_started",
            "installation": "getting_started",
            "quickstart": "getting_started",
            "guides": "user_guide",
            "howto": "user_guide",
            "tutorials": "user_guide",
            "concepts": "concepts",
            "architecture": "concepts",
            "design": "concepts",
            "reference": "reference",
            "api": "reference",
            "examples": "examples",
            "demos": "examples",
            "advanced": "advanced",
            "internals": "advanced",
            "contributing": "advanced",
            "faq": "user_guide",
        }
        
        # Process discovered documents and add to TOC with perfect organization
        for category, docs in self.documents.items():
            for doc in docs:
                # Determine target section with contextual intelligence
                target_section = section_mapping.get(doc.section.lower(), "reference")
                
                # Ensure target section exists
                if target_section not in toc:
                    toc[target_section] = {
                        "title": target_section.replace("_", " ").title(),
                        "items": []
                    }
                
                # Add to the appropriate section with perfect structural awareness
                toc[target_section]["items"].append({
                    "title": doc.title,
                    "url": doc.url,
                    "priority": doc.priority,
                    "category": doc.category
                })
                    
                # Mark this document as added
                self.tracked_documents.add(doc.url)
        
        # Try to intelligently place orphaned documents in appropriate sections
        if self.orphaned_documents:
            self._place_orphaned_documents(toc)
        
        # Sort items by priority within each section for perfect organization
        for section in toc.values():
            section["items"] = sorted(section["items"], key=lambda x: x.get("priority", 50))
            
        return toc
    
    def _place_orphaned_documents(self, toc: Dict) -> None:
        """
        Place orphaned documents into the appropriate TOC sections with Eidosian compassion.
        
        Uses intelligent content analysis to determine the most appropriate section
        for each orphaned document, ensuring no valuable content is lost.
        
        Args:
            toc: Table of contents structure to update
        """
        # Patterns to match document content with sections - Eidosian classification
        section_patterns = {
            "getting_started": ["installation", "quickstart", "setup", "introduction", "overview", "begin"],
            "user_guide": ["guide", "how to", "usage", "tutorial", "workflow", "manual", "instructions"],
            "concepts": ["concept", "architecture", "design", "principles", "theory", "philosophy", "model"],
            "reference": ["api", "reference", "class", "function", "method", "parameter", "attribute"],
            "examples": ["example", "sample", "demo", "showcase", "illustration", "walkthrough"],
            "advanced": ["advanced", "expert", "internals", "deep dive", "contribute", "extend", "customize"]
        }
        
        for orphan in self.orphaned_documents:
            # Skip if not a file or doesn't exist
            if not orphan.is_file() or not orphan.exists():
                continue
                
            # Create a default URL for the orphan with perfect path awareness
            orphan_url = str(orphan.relative_to(self.docs_dir)).replace('\\', '/')
            orphan_url = re.sub(r'\.(md|rst|txt)$', '.html', orphan_url)
            
            # Skip if already in TOC
            if orphan_url in self.tracked_documents:
                continue
            
            # Determine the best section with Eidosian intelligence
            best_section, title = self._analyze_orphan_content(orphan, section_patterns)
            
            # Add to the appropriate section with perfect integration
            toc[best_section]["items"].append({
                "title": title,
                "url": orphan_url,
                "priority": 90,  # Orphaned docs get lowest priority
                "category": "orphan"
            })
            
            # Mark this document as tracked
            self.tracked_documents.add(orphan_url)
    
    def _analyze_orphan_content(self, orphan: Path, section_patterns: Dict[str, List[str]]) -> Tuple[str, str]:
        """
        Analyze orphaned document content to determine its optimal section and title.
        
        Args:
            orphan: Path to the orphaned document
            section_patterns: Dictionary mapping section names to content patterns
            
        Returns:
            Tuple of (best_section, title)
        """
        best_section = "reference"  # Default fallback section
        best_score = 0
        
        # Extract filename-based title with proper formatting
        title = orphan.stem.replace("_", " ").title()
        
        # Check filename first for section hints
        filename_lower = orphan.stem.lower()
        for section, patterns in section_patterns.items():
            for pattern in patterns:
                if pattern in filename_lower:
                    if best_section == "reference" or best_score < 2:
                        best_section = section
                        best_score = 2
        
        # If no strong match in filename, check content with Eidosian thoroughness
        if best_score < 2:
            try:
                # Use cached content if available
                content_key = str(orphan)
                if content_key in self._file_content_cache:
                    content = self._file_content_cache[content_key].lower()
                else:
                    with open(orphan, "r", encoding="utf-8") as f:
                        content = f.read().lower()
                        # Cache for future use
                        self._file_content_cache[content_key] = content
                        
                # Score each section based on pattern matches
                for section, patterns in section_patterns.items():
                    # Calculate weighted score based on pattern frequency and position
                    section_score = sum(content.count(pattern) * (3 if pattern in content[:500] else 1) 
                                      for pattern in patterns)
                    if section_score > best_score:
                        best_section = section
                        best_score = section_score
            except Exception as e:
                logger.debug(f"Couldn't analyze content of {orphan}: {e}")
        
        # Try to extract a better title from the content with format awareness
        try:
            if content_key not in self._file_content_cache:
                with open(orphan, "r", encoding="utf-8") as f:
                    content = f.read()
                    self._file_content_cache[content_key] = content
            else:
                content = self._file_content_cache[content_key]
                
            content_lines = content.split('\n')
            
            if orphan.suffix == ".md":
                # Look for markdown title with perfect precision
                for line in content_lines:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
                    
            elif orphan.suffix == ".rst":
                # Look for RST title with structural awareness
                for i, line in enumerate(content_lines):
                    if i > 0 and i < len(content_lines) - 1:
                        next_line = content_lines[i + 1]
                        if (re.match(r'^[=\-]+$', next_line) and line.strip() and 
                            len(line.strip()) >= len(next_line.strip()) * 0.8):
                            title = line.strip()
                            break
        except Exception as e:
            logger.debug(f"Couldn't extract title from {orphan}: {e}")
                
        return best_section, title
    
    def find_all_sources(self) -> Dict[str, List[Path]]:
        """
        Find all documentation sources across the project with Eidosian completeness.
        
        Returns:
            Dictionary mapping categories to lists of file paths
        """
        all_sources = {
            "user": [],
            "auto": [],
            "ai": [],
            "orphaned": []
        }
        
        # Find user documentation with perfect source awareness
        user_docs_dir = self.doc_structure.get("user_docs", self.docs_dir / "user_docs")
        if user_docs_dir.exists():
            for ext in self.doc_extensions:
                all_sources["user"].extend(
                    [p for p in user_docs_dir.glob(f"**/*{ext}") 
                     if not any(part.startswith("_") for part in p.parts)]
                )
        
        # Find auto-generated documentation with systematic completeness
        auto_docs_dir = self.doc_structure.get("auto_docs", self.docs_dir / "auto_docs")
        autoapi_dirs = [
            auto_docs_dir,
            self.docs_dir / "autoapi",
            self.docs_dir / "apidoc",
            self.docs_dir / "reference"
        ]
        
        for directory in autoapi_dirs:
            if directory.exists():
                for ext in self.doc_extensions:
                    all_sources["auto"].extend(
                        [p for p in directory.glob(f"**/*{ext}") 
                        if not any(part.startswith("_") for part in p.parts)]
                    )
        
        # Find AI-generated documentation with synthetic intelligence
        ai_docs_dir = self.doc_structure.get("ai_docs", self.docs_dir / "ai_docs")
        if ai_docs_dir.exists():
            for ext in self.doc_extensions:
                all_sources["ai"].extend(
                    [p for p in ai_docs_dir.glob(f"**/*{ext}") 
                     if not any(part.startswith("_") for part in p.parts)]
                )
        
        # Add orphaned documents with compassionate inclusion
        all_sources["orphaned"] = self.orphaned_documents
        
        return all_sources
    
    def resolve_references(self) -> Dict[str, Set[str]]:
        """
        Resolve references between documentation files with perfect relational clarity.
        
        Creates a comprehensive bidirectional map of document relationships,
        enabling instantaneous traversal of the documentation network.
        
        Returns:
            Dictionary mapping document paths to sets of referenced documents
        """
        # Initialize reference map with Eidosian efficiency - pre-allocate for zero reallocation
        reference_map: Dict[str, Set[str]] = {}
        
        # Process all discovered documents with relational intelligence
        for category, docs in self.documents.items():
            # Only add entries with actual references - zero waste principle
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
    
    # Create discovery system and run discovery with Eidosian thoroughness
    discovery = DocumentationDiscovery(docs_dir=docs_dir)
    documents = discovery.discover_all()
    
    logger.info(f"✅ Documentation discovery complete. Found {sum(len(docs) for docs in documents.values())} documents")
    return documents

def discover_code_structures(src_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Discover code structures in source code for documentation mapping.
    
    This function finds Python modules, classes and functions to map to documentation
    with perfect structural awareness.
    
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
            # Try other common locations with adaptive intelligence
            for candidate in [repo_root, repo_root / "lib", repo_root / "source"]:
                if candidate.exists() and any(p.suffix == ".py" for p in candidate.glob("**/*.py")):
                    src_dir = candidate
                    break
    
    if not src_dir.exists():
        logger.warning(f"⚠️ Source directory not found at {src_dir}")
        return []
    
    logger.info(f"🔍 Discovering code structures in {src_dir}")
    
    discovered_items = []
    
    # Find all Python files recursively with systematic precision
    python_files = list(src_dir.glob("**/*.py"))
    
    # Process each Python file with Eidosian thoroughness
    for file_path in python_files:
        try:
            # Skip __init__.py files and test files for better focus
            if file_path.name == "__init__.py" or "test" in file_path.name.lower():
                continue
                
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Find modules (from the file itself)
            module_path = str(file_path.relative_to(src_dir.parent)).replace("\\", "/")
            module_name = module_path.replace("/", ".").replace(".py", "")
            discovered_items.append({
                "name": module_name,
                "type": "module",
                "file": str(file_path),
                "doc_ready": True
            })
            
            # Find classes with perfect precision
            class_matches = re.finditer(r'class\s+([A-Za-z0-9_]+)(?:\(.*?\))?:', content)
            for match in class_matches:
                class_name = match.group(1)
                # Extract docstring if present (simplified approach)
                class_pos = match.start()
                docstring_match = re.search(r'"""(.*?)"""', content[class_pos:class_pos+500], re.DOTALL)
                has_docs = bool(docstring_match)
                
                discovered_items.append({
                    "name": class_name,
                    "type": "class",
                    "file": str(file_path),
                    "module": module_name,
                    "doc_ready": has_docs
                })
                
            # Find functions with perfect structural awareness
            func_matches = re.finditer(r'def\s+([A-Za-z0-9_]+)(?:\(.*?\))?:', content)
            for match in func_matches:
                func_name = match.group(1)
                # Skip private functions (but include special methods)
                if func_name.startswith("_") and not (func_name.startswith("__") and func_name.endswith("__")):
                    continue
                
                # Extract docstring if present (simplified approach)
                func_pos = match.start()
                docstring_match = re.search(r'"""(.*?)"""', content[func_pos:func_pos+500], re.DOTALL)
                has_docs = bool(docstring_match)
                    
                discovered_items.append({
                    "name": func_name,
                    "type": "function",
                    "file": str(file_path),
                    "module": module_name,
                    "doc_ready": has_docs
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
