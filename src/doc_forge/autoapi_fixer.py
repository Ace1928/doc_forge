#!/usr/bin/env python3
# 🌀 Eidosian Universal AutoAPI Fixer
"""
Universal AutoAPI Fixer - Repairing AutoAPI-Generated Documentation

This script identifies and fixes common issues in documentation files
generated by the Sphinx AutoAPI extension. It handles:
    • Duplicate object descriptions
    • Broken or ambiguous cross-references
    • Inline literal inconsistencies
    • Unexpected indentation in docstrings
    • Block quote formatting

All logic is modular, reusable, and extensible for multiple projects.
No references to specific modules or clients—this aims for universal coverage.

Following Eidosian principles of:
    • Precision as Style
    • Structure as Control
    • Recursive Refinement
"""
import re
import logging
from pathlib import Path
from typing import Set, DefaultDict, List
from collections import defaultdict

# 📊 Structured Logging - Self-Awareness Foundation
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
)
logger = logging.getLogger("eidosian_docs.autoapi_fixer")

class AutoAPIFixer:
    """
    Universal AutoAPI Fixer for Sphinx-generated documentation.

    Attributes:
        docs_dir (Path): Path to the docs directory containing AutoAPI artifacts.
        autoapi_dir (Path): Subdirectory where Sphinx AutoAPI output is placed.
        fixed_count (int): Counter for how many files have been updated.
        exceptions_list (Set[str]): Collected names of exception classes from the codebase.
        duplicates_seen (DefaultDict[str, int]): Tracks repeated directive headings for universal deduplication.
    """
    
    def __init__(self, docs_dir: Path):
        self.docs_dir: Path = docs_dir
        self.autoapi_dir: Path = docs_dir / "autoapi"  # 🔍 Where AutoAPI dumps its treasures
        self.fixed_count: int = 0  # 🧮 Track our victories
        self.exceptions_list: Set[str] = set()  # 🧩 Collection of unique exception classes
        self.duplicates_seen: DefaultDict[str, int] = defaultdict(int)  # 🔄 Track repeated directives
        
    def discover_exceptions(self) -> None:
        """
        Discovers all exception classes defined in the docs under AutoAPI.
        This approach is universal; it scans for any 'py:class' or 'py:exception' directives
        ending with 'Error' or 'Exception'.
        """
        for rst_file in self.autoapi_dir.glob("**/*.rst"):
            if not rst_file.is_file():
                continue
            try:
                content = rst_file.read_text(encoding="utf-8")
                matches = re.finditer(
                    r'^\.\. py:(?:class|exception):: ([A-Za-z0-9_]+(?:Error|Exception))',
                    content,
                    re.MULTILINE
                )
                for m in matches:
                    self.exceptions_list.add(m.group(1))
            except Exception as e:
                logger.error(f"Error reading {rst_file}: {e}")
        logger.info(f"🔍 Discovered {len(self.exceptions_list)} exception classes in total.")
        
    def fix_all_files(self) -> int:
        """
        Fixes all AutoAPI-generated RST files in the docs directory.

        Returns:
            int: Number of files successfully fixed.
        """
        if not self.autoapi_dir.exists():
            logger.warning("AutoAPI directory does not exist. No files to fix.")
            return 0
        
        # First discover all exception classes
        self.discover_exceptions()
        
        # Process all RST files
        for rst_file in self.autoapi_dir.glob("**/*.rst"):
            if self.fix_file(rst_file):
                self.fixed_count += 1
        
        logger.info(f"✨ Fixed {self.fixed_count} files in total.")
        return self.fixed_count
    
    def fix_file(self, file_path: Path) -> bool:
        """
        Applies all known fixes to the given RST file.

        Args:
            file_path (Path): Path to the RST file.

        Returns:
            bool: True if file was modified, False otherwise.
        """
        try:
            original_content = file_path.read_text(encoding="utf-8")
            new_content = self.fix_duplicate_descriptions(original_content)
            new_content = self.fix_cross_references(new_content)
            new_content = self.fix_inline_literals(new_content)
            new_content = self.fix_unexpected_indentation(new_content)
            new_content = self.fix_block_quotes(new_content)
            
            if new_content != original_content:
                file_path.write_text(new_content, encoding="utf-8")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to fix {file_path}: {e}")
            return False
    
    def fix_duplicate_descriptions(self, content: str) -> str:
        """
        Detects repeated directives (.. py:*:: <object>) and marks subsequent occurrences
        with :noindex:. Works universally, regardless of object name.

        Args:
            content (str): The RST content to analyze.

        Returns:
            str: Updated content with deduplicated directives.
        """
        # Extract all directive lines
        directive_pattern = r'^\.\. py:[a-z]+:: (.+?)$'
        
        # Reset directive counts for this document
        directive_counts: DefaultDict[str, int] = defaultdict(int)
        
        lines = content.split('\n')
        updated_lines: list[str] = []
        
        for line in lines:
            match = re.match(directive_pattern, line)
            if match:
                obj_name = match.group(1).strip()
                directive_counts[obj_name] += 1
                
                # If this is a duplicate directive, add :noindex:
                if directive_counts[obj_name] > 1 and ':noindex:' not in line:
                    line = f"{line}\n   :noindex:"
            
            updated_lines.append(line)
        
        return '\n'.join(updated_lines)
    
    def fix_cross_references(self, content: str) -> str:
        """
        Replaces ambiguous exception references with fully qualified references.
        Adds appropriate module prefix to exception class references.

        Args:
            content (str): RST content to update.

        Returns:
            str: Content with updated cross-reference directives.
        """
        if not self.exceptions_list:
            return content
            
        # For modularity, we'll detect what looks like a module prefix pattern
        # from the content and use it consistently
        module_prefix = "my_project.exceptions."  # Default fallback
        
        # Try to detect module pattern from existing qualified references
        module_match = re.search(r':(?:class|exc):`([a-zA-Z0-9_.]+)\.([A-Za-z0-9_]+(?:Error|Exception))`', content)
        if module_match:
            module_prefix = f"{module_match.group(1)}."
            
        # Replace cross-references to exception classes with fully qualified references
        for exception in self.exceptions_list:
            # Pattern for inline references
            pattern = rf':(?:class|exc):`({exception})`'
            content = re.sub(
                pattern,
                f':class:`{module_prefix}\\1`',
                content
            )
            
            # Pattern for raises directives
            pattern = rf':raises\s+({exception}):'
            content = re.sub(
                pattern,
                f':raises {module_prefix}\\1:',
                content
            )
            
            # Pattern for references in parameter/return type documentation
            pattern = rf'([^\w.])({exception})([^\w`])'
            content = re.sub(
                pattern,
                f'\\1{module_prefix}\\2\\3',
                content
            )
        
        return content
    
    def fix_inline_literals(self, content: str) -> str:
        """
        Pairs unmatched backticks and handles lines with odd backtick counts.

        Args:
            content (str): Original content with potential inline literal issues.

        Returns:
            str: Patched content with balanced backticks.
        """
        # Pattern to find unmatched backticks
        lines = content.split('\n')
        for i in range(len(lines)):
            # Count backticks in line
            count = lines[i].count('`')
            if count % 2 == 1:  # Odd number of backticks - likely an issue
                # Look for opening backtick without matching closing one
                if '`' in lines[i] and lines[i].rfind('`') == lines[i].find('`'):
                    lines[i] += '`'  # Add closing backtick
                    
                # Special case for sphinx rst equations
                if ':math:`' in lines[i] and not lines[i].endswith('`'):
                    lines[i] += '`'
        
        # Fix backtick spans across lines (common in docstring conversion)
        for i in range(len(lines) - 1):
            if lines[i].count('`') % 2 == 1 and lines[i+1].count('`') % 2 == 1:
                # If line ends with backtick and next starts with backtick, merge them
                if lines[i].endswith('`') and lines[i+1].startswith('`'):
                    lines[i] = lines[i][:-1]
                    lines[i+1] = lines[i+1][1:]
        
        return '\n'.join(lines)  # Fixed the syntax error here
    
    def fix_unexpected_indentation(self, content: str) -> str:
        """
        Addresses accidental or inconsistent indentation in docstring lines
        and corrects code-block indentation inside example sections.

        Args:
            content (str): Input RST docstring content.

        Returns:
            str: RST with standardized indentation for blocks.
        """
        # Look for lines that have an unexpected indentation
        pattern = r'(^\s+)(\S.*?)\n\s{4,}(\S)'
        content = re.sub(pattern, r'\1\2\n\1    \3', content, flags=re.MULTILINE)
        
        # Fix indentation of code examples
        lines = content.split('\n')
        in_example = False
        in_code_block = False
        result: List[str] = []
        
        for i, line in enumerate(lines):
            # Detect example sections
            if 'Example' in line and ':' in line:
                in_example = True
                result.append(line)
                # Make sure we have a blank line after Example:
                if i+1 < len(lines) and lines[i+1].strip():
                    result.append('')
                continue
                
            # Fix code blocks within examples
            if in_example and line.strip() == '::':
                in_code_block = True
                result.append(line)
                # Make sure we have a blank line after ::
                if i+1 < len(lines) and lines[i+1].strip():
                    result.append('')
                continue
                
            # Ensure code blocks have proper indentation
            if in_code_block and line.strip():
                # End code block on first non-indented line
                if not line.startswith('    '):
                    in_code_block = False
                    in_example = False
                    result.append(line)
                    continue
                
                # Fix inconsistent indentation
                indent = len(line) - len(line.lstrip())
                if 0 < indent < 4:
                    result.append('    ' + line.lstrip())
                    continue
            
            result.append(line)
                
        return '\n'.join(result)
    
    def fix_block_quotes(self, content: str) -> str:
        """
        Ensures block quotes and literal blocks have standard spacing.

        Args:
            content (str): RST text to process.

        Returns:
            str: Normalized content with corrected blank lines around quotes/blocks.
        """
        # Fix block quotes that don't have proper blank lines after them
        pattern = r'(\n\s+[^\s].*\n)([^\s])'
        content = re.sub(pattern, r'\1\n\2', content)
        
        # Ensure blank lines before and after literal blocks
        pattern = r'([^\n])::\n(\S)'
        content = re.sub(pattern, r'\1::\n\n\2', content)
        
        return content


def main() -> None:
    """Entry point for the universal AutoAPI fixer."""
    import sys
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    docs_dir = repo_root / "docs"
    
    fixer = AutoAPIFixer(docs_dir)
    fixed_count = fixer.fix_all_files()
    
    logger.info(f"🔧 Universal AutoAPI Fixer Complete. Total files fixed: {fixed_count}")
    sys.exit(0 if fixed_count > 0 else 1)

if __name__ == "__main__":
    main()
