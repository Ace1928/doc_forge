#!/usr/bin/env python3
# 🌀 Eidosian Documentation Discovery System
"""
Source Discovery - Adaptive Documentation Architecture

This module implements a universal discovery system for documentation sources,
analyzing content from multiple formats and organizing it into a coherent
structure with perfect precision and adaptability.

Following Eidosian principles of:
- Contextual Integrity: Documents connected by relationship, not location
- Flow Like a River: Seamless integration of multiple sources
- Structure as Control: Organization that reveals meaning
- Self-Awareness: System adapts to content patterns
"""

import os
import sys
import re
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union
import yaml
import json
from dataclasses import dataclass, field
from datetime import datetime

# 📊 Structured Logging - Self-Awareness Foundation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("eidosian_docs.discovery")

@dataclass
class DocumentMetadata:
    """
    Metadata extracted from document content with recursive refinement.
    Each document tells a story - we just need to listen carefully! 📚
    """
    path: Path  # 🛣️ Where to find this document
    title: str = ""  # 📝 What this document calls itself
    category: str = "uncategorized"  # 🏷️ How we classify this content
    tags: List[str] = field(default_factory=list)  # 🏷️ Specialized markers
    priority: int = 50  # 🔢 Importance (higher = more important)
    date: Optional[datetime] = None  # 📅 When this document was born
    summary: str = ""  # 💬 TL;DR version
    related: List[str] = field(default_factory=list)  # 🔗 Connected documents
    
    # Document format and processing info
    format: str = ""  # 📄 md, rst, py, etc.
    has_frontmatter: bool = False  # 🎭 YAML/metadata at the top?
    is_api_doc: bool = False  # 🧩 Is this API documentation?
    toc_depth: int = 2  # 📑 How deep should the TOC go?
    
    def extract_from_content(self, content: str) -> None:
        """
        Extract metadata from document content using pattern recognition.
        Like a detective reading between the lines! 🕵️
        """
        # Format detection - what kind of document are we dealing with?
        self.format = self.path.suffix.lstrip('.').lower()
        
        # Title extraction strategies by format
        if self.format == 'md':
            # Look for markdown title patterns - the headline act!
            title_match = re.search(r'^# (.*?)$', content, re.MULTILINE)
            if title_match:
                self.title = title_match.group(1).strip()
            
            # Check for YAML frontmatter - the hidden treasure
            frontmatter_match = re.search(r'^---\s*(.*?)\s*---', content, re.DOTALL)
            if frontmatter_match:
                self.has_frontmatter = True
                try:
                    frontmatter = yaml.safe_load(frontmatter_match.group(1))
                    # Update metadata from frontmatter - trust the author's intent
                    if isinstance(frontmatter, dict):
                        if 'title' in frontmatter:
                            self.title = frontmatter['title']
                        if 'category' in frontmatter:
                            self.category = frontmatter['category']
                        if 'tags' in frontmatter:
                            self.tags = frontmatter['tags']
                        if 'priority' in frontmatter:
                            self.priority = int(frontmatter['priority'])
                        if 'date' in frontmatter:
                            self.date = frontmatter['date']
                        if 'summary' in frontmatter:
                            self.summary = frontmatter['summary']
                except Exception as e:
                    logger.warning(f"📛 Error parsing frontmatter in {self.path}: {e}")
        
        elif self.format == 'rst':
            # Look for RST title patterns
            title_match = re.search(r'^(.*?)\n[=]+\s*$', content, re.MULTILINE)
            if title_match:
                self.title = title_match.group(1).strip()
                
            # Extract directive metadata
            meta_matches = re.findall(r'^\.\. ([a-z]+):: (.*)$', content, re.MULTILINE)
            for directive, value in meta_matches:
                if directive == 'category':
                    self.category = value.strip()
                elif directive == 'tags':
                    self.tags = [t.strip() for t in value.split(',')]
                elif directive == 'priority':
                    try:
                        self.priority = int(value.strip())
                    except ValueError:
                        pass
        
        elif self.format == 'py':
            # Check if it's an API doc
            self.is_api_doc = True
            
            # Extract module or class name as title
            module_match = re.search(r'^class\s+([A-Za-z0-9_]+)', content, re.MULTILINE)
            if module_match:
                self.title = module_match.group(1)
            else:
                # Try to get module name
                module_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if module_match:
                    docstring = module_match.group(1).strip()
                    first_line = docstring.split('\n')[0].strip()
                    self.title = first_line
                    
                    # Try to extract summary from docstring
                    if len(docstring.split('\n')) > 1:
                        self.summary = '\n'.join(docstring.split('\n')[1:3]).strip()
        
        # Use filename as fallback title - when all else fails
        if not self.title:
            self.title = self.path.stem.replace('_', ' ').title()
            
        # Capitalize first letter of title - proper etiquette!
        if self.title:
            self.title = self.title[0].upper() + self.title[1:]
    
    @property
    def url(self) -> str:
        """Generate the URL for this document."""
        if self.is_api_doc:
            # API docs have a special URL format
            relative_path = self.path.relative_to(self.path.parent)
            module_path = str(relative_path).replace('/', '.').replace('.py', '')
            return f"autoapi/{module_path}/index.html"
        
        # Regular docs just use the path relative to docs
        return str(self.path).replace('.md', '.html').replace('.rst', '.html')


class DocumentationDiscovery:
    """
    Universal documentation discovery system implementing Eidosian principles.
    
    This class discovers, categorizes, and organizes documentation from multiple
    sources into a coherent structure that adapts to the content patterns.
    """
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.docs_dir = repo_root / 'docs'
        self.categories = {}
        self.tracked_documents: Set[str] = set()  # Track documents to avoid duplicates
        self.orphaned_documents: List[Path] = []  # Track orphaned documents
        
    def discover_all_documents(self) -> Dict[str, List[DocumentMetadata]]:
        """
        Discover all documentation sources and organize them into categories.
        Returns a dictionary of category -> document list.
        """
        # Start from conf.py's DOC_MAPPING configuration
        documents = {}
        
        # Get conf.py location
        conf_path = self.docs_dir / 'conf.py'
        if not conf_path.exists():
            logger.warning(f"conf.py not found at {conf_path}")
            return documents
        
        # Parse conf.py to extract DOC_MAPPING
        with open(conf_path, 'r') as f:
            conf_content = f.read()
            
        # Check if using DOC_MAPPING (new style) or DOC_SOURCES (old style)
        doc_mapping_match = re.search(r'DOC_MAPPING\s*=\s*{', conf_content, re.DOTALL)
        doc_sources_match = re.search(r'DOC_SOURCES\s*=\s*{', conf_content, re.DOTALL)
        
        if doc_mapping_match:
            # Process DOC_MAPPING structure
            for category in ['core_docs', 'api_docs', 'features', 'guides', 'getting_started']:
                logger.info(f"Processing category: {category}")
                
                # Extract paths from DOC_MAPPING items that belong to this section
                pattern = rf'"section":\s*"{category}".*?"path":\s*.*?/\s*"([^"]*)"'
                path_matches = re.finditer(pattern, conf_content, re.DOTALL)
                
                for path_match in path_matches:
                    rel_path = path_match.group(1).strip('"')
                    source_path = self.repo_root / rel_path
                    
                    # Extract patterns 
                    patterns_match = re.search(rf'"patterns":\s*\[(.*?)\]', conf_content)
                    patterns = ["*.md", "*.rst", "*.py"]  # Default patterns
                    
                    if patterns_match:
                        patterns_str = patterns_match.group(1)
                        extracted_patterns = [p.strip(' "\'') for p in patterns_str.split(',')]
                        if extracted_patterns:
                            patterns = extracted_patterns
                    
                    # Process this path
                    doc_list = self._discover_in_path(source_path, patterns, category)
                    if doc_list:
                        if category not in documents:
                            documents[category] = []
                        documents[category].extend(doc_list)
                        
        elif doc_sources_match:
            # Fall back to legacy DOC_SOURCES format
            # Extract DOC_SOURCES dictionary
            for category in ['core', 'api', 'examples', 'user_generated']:
                logger.info(f"Processing category: {category}")
                # Find the category in conf_content
                category_match = re.search(rf'"{category}":\s*{{(.*?)}},', conf_content, re.DOTALL)
                if category_match:
                    category_config = category_match.group(1)
                    
                    # Extract path
                    path_match = re.search(r'"path":\s*REPO_ROOT\s*/\s*"([^"]*)"', category_config)
                    if not path_match and 'REPO_ROOT / "' not in category_config:
                        path_match = re.search(r'"path":\s*REPO_ROOT\s*/\s*([^,}]+)', category_config)
                        
                    if path_match:
                        rel_path = path_match.group(1).strip('"')
                        source_path = self.repo_root / rel_path
                        
                        # Extract patterns
                        patterns_match = re.search(r'"patterns":\s*\[(.*?)\]', category_config)
                        if patterns_match:
                            patterns_str = patterns_match.group(1)
                            patterns = [p.strip(' "\'') for p in patterns_str.split(',')]
                            
                            # Map old categories to new ones
                            mapped_category = {
                                'core': 'core_docs',
                                'api': 'api_docs',
                                'examples': 'guides',
                                'user_generated': 'features'
                            }.get(category, category)
                            
                            # Process this category
                            doc_list = self._discover_in_path(source_path, patterns, mapped_category)
                            if doc_list:
                                if mapped_category not in documents:
                                    documents[mapped_category] = []
                                documents[mapped_category].extend(doc_list)
        else:
            logger.warning("Neither DOC_MAPPING nor DOC_SOURCES found in conf.py")
        
        # Find orphaned documents in the docs directory
        self._find_orphaned_documents()
        
        return documents
    
    def _discover_in_path(self, path: Path, patterns: List[str], category: str) -> List[DocumentMetadata]:
        """Discover documents in a specific path matching the given patterns."""
        if not path.exists():
            logger.warning(f"Path does not exist: {path}")
            return []
            
        documents = []
        for pattern in patterns:
            for file_path in path.glob(f"**/{pattern}"):
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create metadata object
                    metadata = DocumentMetadata(path=file_path, category=category)
                    metadata.extract_from_content(content)
                    
                    documents.append(metadata)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
        
        return documents
    
    def _find_orphaned_documents(self) -> None:
        """Find documents in the docs directory that might be orphaned."""
        # Common documentation file patterns
        patterns = ["*.md", "*.rst", "*.txt"]
        excluded_dirs = ["_build", "_static", "_templates", "__pycache__"]
        
        for pattern in patterns:
            for file_path in self.docs_dir.glob(f"**/{pattern}"):
                # Skip files in excluded directories
                if any(excluded in str(file_path) for excluded in excluded_dirs):
                    continue
                
                # Add to orphaned documents list for later processing
                rel_path = file_path.relative_to(self.docs_dir)
                self.orphaned_documents.append(file_path)
    
    def generate_toc_structure(self, documents: Dict[str, List[DocumentMetadata]]) -> Dict:
        """
        Generate a Table of Contents structure from the discovered documents.
        This can be used to build the sidebar and navigation.
        """
        toc = {
            "getting_started": {
                "caption": "📚 Getting Started",
                "items": []
            },
            "core_docs": {
                "caption": "🛠️ Core Documentation", 
                "items": []
            },
            "features": {
                "caption": "🔄 Features & Capabilities",
                "items": []
            },
            "guides": {
                "caption": "🧠 Guides & References",
                "items": []
            },
            "api_docs": {
                "caption": "🧩 API Endpoints",
                "items": []
            },
            "examples": {
                "caption": "📋 Examples",
                "items": []
            }
        }
        
        # Create a set to track added documents to avoid duplication
        self.tracked_documents = set()
        
        # Map documents to TOC sections based on category and content
        for category, docs in documents.items():
            for doc in docs:
                # Skip if the same document has already been added (by URL)
                if doc.url in self.tracked_documents:
                    continue
                    
                # Determine which section this document belongs in
                target_section = category  # Default to document's own category
                
                # Override based on content analysis
                if doc.category == 'getting_started' or category == 'core_docs' and 'introduction' in doc.title.lower():
                    target_section = "getting_started"
                elif category == 'api_docs' or doc.is_api_doc:
                    target_section = "api_docs"
                elif "feature" in doc.tags or "capability" in doc.tags:
                    target_section = "features"
                elif "guide" in doc.tags or "reference" in doc.tags or "example" in doc.tags:
                    target_section = "guides"
                
                # Make sure the section exists in our TOC
                if target_section not in toc:
                    target_section = "core_docs"  # Default fallback
                    
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
        """Place orphaned documents into the appropriate toc sections based on their content."""
        for orphan in self.orphaned_documents[:]:
            try:
                # Skip if it's a special file that shouldn't be included
                if orphan.name == 'requirements.txt':
                    continue
                    
                # Read the orphan file
                with open(orphan, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create a stripped relative URL for comparison
                rel_url = str(orphan.relative_to(self.docs_dir)).replace('.md', '.html').replace('.rst', '.html')
                
                # Skip if already in tracked documents
                if rel_url in self.tracked_documents:
                    continue
                
                # Extract title from content
                title = orphan.stem.replace('_', ' ').title()
                title_match = re.search(r'^# (.*?)$', content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1)
                
                # Determine appropriate section
                section_key = "guides"  # Default to guides
                
                # Check content to determine best section
                if 'principle' in content.lower() or 'eidosian' in content.lower():
                    section_key = "getting_started"
                elif 'api' in content.lower() or 'endpoint' in content.lower():
                    section_key = "api_docs"
                elif 'feature' in content.lower() or 'capability' in content.lower():
                    section_key = "features"
                elif 'installation' in content.lower() or 'setup' in content.lower() or 'intro' in content.lower():
                    section_key = "getting_started"
                
                # Add to appropriate section
                toc[section_key]["items"].append({
                    "title": title,
                    "url": rel_url,
                    "priority": 99  # Lower priority for orphaned docs
                })
                
                # Mark as tracked
                self.tracked_documents.add(rel_url)
                logger.info(f"Placed orphaned document {orphan.name} in {section_key}")
                
            except Exception as e:
                logger.warning(f"Error processing orphaned document {orphan}: {e}")
    
    def generate_sphinx_toctree(self, toc_structure: Dict) -> Dict[str, str]:
        """
        Generate Sphinx toctree directives from the TOC structure.
        Returns a dictionary mapping section names to toctree strings.
        """
        toctrees = {}
        tracked_urls = set()  # Ensure no duplicates across sections
        
        for section_name, section_data in toc_structure.items():
            toctree = f"""
.. toctree::
   :maxdepth: 2
   :caption: {section_data['caption']}

"""
            items_added = False
            
            for item in section_data["items"]:
                # Remove .html extension and convert to relative path
                url = item["url"].replace('.html', '')
                
                # Skip if this URL has already been added to another toctree
                if url in tracked_urls:
                    continue
                    
                toctree += f"   {url}\n"
                tracked_urls.add(url)
                items_added = True
            
            # Only add toctree if it has items
            if items_added:
                toctrees[section_name] = toctree
            
        return toctrees
    
    def write_index_with_toctrees(self, toctrees: Dict[str, str]) -> None:
        """
        Write the index.rst file with the generated toctrees.
        """
        index_path = self.docs_dir / "index.rst"
        
        # Read existing index to preserve content
        existing_content = ""
        if index_path.exists():
            with open(index_path, "r") as f:
                existing_content = f.read()
                
            # Extract the part before the toctrees
            intro_match = re.search(r'^(.*?)\.\.(?:\s+toctree::|$)', existing_content, re.DOTALL)
            if intro_match:
                existing_content = intro_match.group(1).strip()
                
        # Create new index content
        index_content = f"""{existing_content}

{toctrees.get("getting_started", "")}

{toctrees.get("core_docs", "")}

{toctrees.get("features", "")}

{toctrees.get("guides", "")}

{toctrees.get("api_docs", "")}
"""
        
        # Write the file
        with open(index_path, "w") as f:
            f.write(index_content)
            
        logger.info(f"✅ Updated index at {index_path}")

    def mark_orphaned_documents(self) -> None:
        """Add :orphan: directive to remaining orphaned documents."""
        for orphan in self.orphaned_documents:
            try:
                # Skip certain files that don't need the orphan directive
                if orphan.suffix not in ['.md', '.rst']:
                    continue
                    
                # Read file content
                with open(orphan, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file already has orphan directive
                if ':orphan:' in content:
                    continue
                    
                # Add orphan directive
                if orphan.suffix == '.md':
                    # For Markdown, add as a comment at the top
                    new_content = f"<!-- :orphan: -->\n\n{content}"
                else:
                    # For RST, add as directive
                    new_content = f":orphan:\n\n{content}"
                    
                # Write updated content
                with open(orphan, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
                logger.info(f"✅ Added orphan directive to {orphan.name}")
                
            except Exception as e:
                logger.warning(f"Error marking orphan document {orphan}: {e}")


if __name__ == "__main__":
    # Run as a standalone script to test
    repo_root = Path(__file__).resolve().parent.parent
    discovery = DocumentationDiscovery(repo_root)
    documents = discovery.discover_all_documents()
    
    # Print summary
    for category, docs in documents.items():
        print(f"Category: {category} - {len(docs)} documents")
        for doc in docs[:5]:  # Show first 5 as example
            print(f"  - {doc.title} ({doc.path})")
        if len(docs) > 5:
            print(f"  ... {len(docs) - 5} more")
    
    # Generate TOC
    toc = discovery.generate_toc_structure(documents)
    toctrees = discovery.generate_sphinx_toctree(toc)
    
    # Check for arguments
    if "--write" in sys.argv:
        discovery.write_index_with_toctrees(toctrees)
        print("\n✅ Index.rst updated")
        
    if "--mark-orphans" in sys.argv:
        discovery.mark_orphaned_documents()
        print(f"\n✅ Marked {len(discovery.orphaned_documents)} orphaned documents")
    
    # If no arguments, print help
    if len(sys.argv) == 1:
        print("\nℹ️ Available commands:")
        print("  --write         : Update index.rst with generated toctrees")
        print("  --mark-orphans  : Mark orphaned documents with :orphan: directive")
