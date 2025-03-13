#!/usr/bin/env python3
# 🌀 Eidosian Documentation Validator
"""
Documentation Validator - Ensuring Documentation Accuracy and Freshness

This module implements validation for the "Living Documentation" concept,
ensuring that documentation stays in sync with code and maintains accuracy
over time with Eidosian precision.

Following Eidosian principles of:
- Self-Awareness as Foundation: Documentation that knows when it's outdated
- Precision as Style: Ensuring exact alignment between code and docs
- Recursive Refinement: Continuous improvement of documentation quality
"""

import ast
import inspect
import importlib
import logging
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union, Callable

# 📊 Self-aware logging system
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
)
logger = logging.getLogger("eidosian_docs.validator")

class DocDiscrepancy:
    """
    Represents a discrepancy between code and documentation.
    Every mismatch is a puzzle waiting to be solved! 🧩
    """
    
    def __init__(self, doc_path: Path, code_path: Path, element_name: str, 
                 discrepancy_type: str, description: str, severity: str = "medium"):
        """
        Initialize a documentation discrepancy.
        
        Args:
            doc_path: Path to the documentation file
            code_path: Path to the code file
            element_name: Name of the affected element (function, class, etc.)
            discrepancy_type: Type of discrepancy (e.g., "signature_mismatch")
            description: Description of the discrepancy
            severity: Severity level ("low", "medium", "high")
        """
        self.doc_path = doc_path
        self.code_path = code_path
        self.element_name = element_name
        self.discrepancy_type = discrepancy_type
        self.description = description
        self.severity = severity
        self.detected_time = datetime.now()
    
    def __str__(self) -> str:
        """String representation with Eidosian clarity."""
        return f"{self.severity.upper()}: {self.discrepancy_type} in {self.element_name} - {self.description}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "doc_path": str(self.doc_path),
            "code_path": str(self.code_path),
            "element_name": self.element_name,
            "discrepancy_type": self.discrepancy_type,
            "description": self.description,
            "severity": self.severity,
            "detected_time": self.detected_time.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocDiscrepancy":
        """Create instance from dictionary."""
        return cls(
            doc_path=Path(data["doc_path"]),
            code_path=Path(data["code_path"]),
            element_name=data["element_name"],
            discrepancy_type=data["discrepancy_type"],
            description=data["description"],
            severity=data["severity"]
        )

class DocValidator:
    """
    Documentation validator that ensures code and docs stay in perfect sync.
    Like a watchful guardian ensuring documentation truth! 🛡️
    """
    
    def __init__(self, repo_root: Path):
        """
        Initialize the documentation validator.
        
        Args:
            repo_root: Repository root directory
        """
        self.repo_root = repo_root
        self.docs_dir = repo_root / "docs"
        self.manifest_path = self.docs_dir / "docs_manifest.json"
        self.discrepancies: List[DocDiscrepancy] = []
        self.validation_rules: Dict[str, Callable] = {
            "check_function_signature_match": self.check_function_signature_match,
            "check_parameter_descriptions": self.check_parameter_descriptions,
            "check_return_value_descriptions": self.check_return_value_descriptions,
            "check_example_validity": self.check_example_validity,
            "check_doc_freshness": self.check_doc_freshness
        }
        
        # Import manifest manager if available
        try:
            from .doc_manifest_manager import DocManifestManager
            self.manifest_manager = DocManifestManager(repo_root)
        except ImportError:
            self.manifest_manager = None
    
    def validate_all_documentation(self, rules: Optional[List[str]] = None) -> List[DocDiscrepancy]:
        """
        Validate all documentation against source code.
        
        Args:
            rules: List of validation rules to apply (default: all)
            
        Returns:
            List of documentation discrepancies
        """
        start_time = time.time()
        logger.info("🔍 Starting documentation validation")
        self.discrepancies = []
        
        # Determine which rules to run
        if rules is None:
            # Get rules from manifest if available
            if self.manifest_manager:
                manifest = self.manifest_manager.get_manifest_data()
                if "living_docs" in manifest and "validation_rules" in manifest["living_docs"]:
                    rules = manifest["living_docs"]["validation_rules"]
            
            # Default rules if still not defined
            if rules is None:
                rules = list(self.validation_rules.keys())
        
        # Get Python modules to validate
        python_modules = self._discover_python_modules()
        
        # Apply validation rules
        for module_path in python_modules:
            # Find corresponding documentation file
            doc_path = self._find_doc_for_module(module_path)
            if doc_path is None:
                logger.debug(f"No documentation found for {module_path}")
                continue
            
            # Apply each enabled rule
            for rule in rules:
                if rule in self.validation_rules:
                    try:
                        self.validation_rules[rule](module_path, doc_path)
                    except Exception as e:
                        logger.error(f"Error applying rule {rule} to {module_path}: {e}")
        
        # Update manifest with validation results if available
        if self.manifest_manager:
            self._update_manifest_with_results()
            
        execution_time = time.time() - start_time
        logger.info(f"✅ Documentation validation completed in {execution_time:.2f}s")
        logger.info(f"📊 Found {len(self.discrepancies)} discrepancies")
        
        return self.discrepancies
    
    def _discover_python_modules(self) -> List[Path]:
        """
        Discover Python modules to validate.
        
        Returns:
            List of Python module paths
        """
        python_modules = []
        
        # Look for Python files in standard locations
        source_dirs = [
            self.repo_root,
            self.repo_root / "src",
            self.repo_root / "doc_forge"
        ]
        
        for source_dir in source_dirs:
            if source_dir.exists():
                for python_file in source_dir.glob("**/*.py"):
                    # Skip __pycache__, tests, etc.
                    if any(part.startswith("__") for part in python_file.parts):
                        continue
                    if "tests" in python_file.parts:
                        continue
                    
                    python_modules.append(python_file)
        
        logger.info(f"🔍 Found {len(python_modules)} Python modules to validate")
        return python_modules
    
    def _find_doc_for_module(self, module_path: Path) -> Optional[Path]:
        """
        Find documentation file for a module.
        
        Args:
            module_path: Path to the module
            
        Returns:
            Path to documentation file or None if not found
        """
        # Check auto-generated API docs
        rel_path = module_path.relative_to(self.repo_root)
        doc_path = self.docs_dir / "auto" / "python" / f"{rel_path.with_suffix('.md')}"
        if doc_path.exists():
            return doc_path
            
        # Check for docs with module name
        module_name = module_path.stem
        for ext in ['.md', '.rst']:
            for pattern in [f"**/{module_name}{ext}", f"**/{module_name.lower()}{ext}"]:
                for match in self.docs_dir.glob(pattern):
                    return match
        
        return None
    
    def _update_manifest_with_results(self) -> None:
        """Update manifest with validation results."""
        if not self.manifest_manager:
            return
            
        # Convert discrepancies to serializable format
        outdated_docs = []
        for discrepancy in self.discrepancies:
            # Add doc path to outdated docs if not already there
            doc_path = str(discrepancy.doc_path.relative_to(self.docs_dir))
            if doc_path not in outdated_docs:
                outdated_docs.append(doc_path)
                
        # Update manifest
        manifest = self.manifest_manager.get_manifest_data()
        if "metadata" in manifest and "validation_status" in manifest["metadata"]:
            manifest["metadata"]["validation_status"]["outdated_docs"] = outdated_docs
            self.manifest_manager.save_manifest()

    def check_function_signature_match(self, module_path: Path, doc_path: Path) -> None:
        """
        Check if function signatures in code match documentation.
        
        Args:
            module_path: Path to the module
            doc_path: Path to the documentation file
        """
        module_ast = self._parse_module(module_path)
        if not module_ast:
            return
            
        with open(doc_path, "r", encoding="utf-8") as f:
            doc_content = f.read()
            
        for node in ast.walk(module_ast):
            if not isinstance(node, ast.FunctionDef):
                continue
                
            # Get function name and signature from code
            func_name = node.name
            signature = self._get_function_signature(node)
            
            # Look for function signature in documentation
            pattern = rf"(?:def|function|method)\s+`?{re.escape(func_name)}`?\s*\(([^\)]*)\)"
            matches = list(re.finditer(pattern, doc_content, re.IGNORECASE))
            
            if not matches:
                self._add_discrepancy(
                    doc_path=doc_path,
                    code_path=module_path,
                    element_name=func_name,
                    discrepancy_type="signature_missing",
                    description=f"Function signature not found in documentation",
                    severity="high"
                )
                continue
                
            # Compare signatures (simplified)
            for match in matches:
                doc_signature = match.group(1).strip()
                if not self._signatures_match(signature, doc_signature):
                    self._add_discrepancy(
                        doc_path=doc_path,
                        code_path=module_path,
                        element_name=func_name,
                        discrepancy_type="signature_mismatch",
                        description=f"Function signature mismatch. Code: ({signature}), Docs: ({doc_signature})",
                        severity="high"
                    )
    
    def check_parameter_descriptions(self, module_path: Path, doc_path: Path) -> None:
        """
        Check if all parameters are documented.
        
        Args:
            module_path: Path to the module
            doc_path: Path to the documentation file
        """
        module_ast = self._parse_module(module_path)
        if not module_ast:
            return
            
        with open(doc_path, "r", encoding="utf-8") as f:
            doc_content = f.read()
            
        for node in ast.walk(module_ast):
            if not isinstance(node, ast.FunctionDef):
                continue
                
            # Get function name and parameters
            func_name = node.name
            params = self._get_function_params(node)
            if not params:
                continue
                
            # Look for parameter descriptions in documentation
            for param in params:
                if param == "self" or param == "cls":
                    continue  # Skip self and cls parameters
                    
                # Check for param documentation patterns
                patterns = [
                    rf"(?:Args|Parameters):[^\n]*\n\s*{re.escape(param)}\s*:",  # Sphinx/Napoleon style
                    rf":param\s+{re.escape(param)}:"  # Sphinx style
                ]
                
                if not any(re.search(pattern, doc_content, re.IGNORECASE | re.DOTALL) for pattern in patterns):
                    self._add_discrepancy(
                        doc_path=doc_path,
                        code_path=module_path,
                        element_name=func_name,
                        discrepancy_type="param_missing",
                        description=f"Parameter '{param}' not documented",
                        severity="medium"
                    )
    
    def check_return_value_descriptions(self, module_path: Path, doc_path: Path) -> None:
        """
        Check if return values are documented.
        
        Args:
            module_path: Path to the module
            doc_path: Path to the documentation file
        """
        module_ast = self._parse_module(module_path)
        if not module_ast:
            return
            
        with open(doc_path, "r", encoding="utf-8") as f:
            doc_content = f.read()
            
        for node in ast.walk(module_ast):
            if not isinstance(node, ast.FunctionDef):
                continue
                
            # Skip functions that don't return anything (no return statements)
            has_return = False
            for sub_node in ast.walk(node):
                if isinstance(sub_node, ast.Return) and sub_node.value is not None:
                    has_return = True
                    break
                    
            if not has_return:
                continue
                
            # Get function name
            func_name = node.name
            
            # Check for return value documentation
            patterns = [
                r"(?:Returns|Return value):[^\n]*\n",  # Sphinx/Napoleon style
                r":return:",  # Sphinx style
                r":rtype:"  # Sphinx style for return type
            ]
            
            if not any(re.search(pattern, doc_content, re.IGNORECASE | re.DOTALL) for pattern in patterns):
                self._add_discrepancy(
                    doc_path=doc_path,
                    code_path=module_path,
                    element_name=func_name,
                    discrepancy_type="return_missing",
                    description="Return value not documented",
                    severity="medium"
                )
    
    def check_example_validity(self, module_path: Path, doc_path: Path) -> None:
        """
        Check if examples in documentation are valid.
        
        Args:
            module_path: Path to the module
            doc_path: Path to the documentation file
        """
        # This is a more complex validation that would typically involve:
        # 1. Extracting code examples from documentation
        # 2. Trying to execute them in a safe environment
        # 3. Checking for errors
        #
        # For now, we'll implement a simplified version that just checks if examples exist
        module_name = module_path.stem
        module_ast = self._parse_module(module_path)
        if not module_ast:
            return
            
        with open(doc_path, "r", encoding="utf-8") as f:
            doc_content = f.read()
            
        # Look for public functions and classes
        public_elements = []
        for node in ast.walk(module_ast):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not node.name.startswith("_"):
                public_elements.append(node.name)
                
        # Check if there's at least one example section
        example_patterns = [
            r"(?:Examples?|Usage):\s*\n\s*```(?:python)?\n",  # Markdown code block after "Example:" or similar
            r"(?:Examples?|Usage):\s*\n\s*::\n",  # RST code block after "Example:" or similar
            r".. code-block::\s*python"  # RST code block directive
        ]
        
        has_examples = any(re.search(pattern, doc_content, re.IGNORECASE) for pattern in example_patterns)
        
        if public_elements and not has_examples:
            self._add_discrepancy(
                doc_path=doc_path,
                code_path=module_path,
                element_name=module_name,
                discrepancy_type="examples_missing",
                description="No examples found in documentation for public API",
                severity="low"
            )
    
    def check_doc_freshness(self, module_path: Path, doc_path: Path) -> None:
        """
        Check if documentation is fresh.
        
        Args:
            module_path: Path to the module
            doc_path: Path to the documentation file
        """
        # Check if code was modified more recently than docs
        code_mtime = datetime.fromtimestamp(module_path.stat().st_mtime)
        doc_mtime = datetime.fromtimestamp(doc_path.stat().st_mtime)
        
        # If code is more than a week newer than docs, flag as potentially outdated
        if code_mtime > doc_mtime and (code_mtime - doc_mtime) > timedelta(days=7):
            self._add_discrepancy(
                doc_path=doc_path,
                code_path=module_path,
                element_name=module_path.stem,
                discrepancy_type="outdated_docs",
                description=f"Documentation is {(code_mtime - doc_mtime).days} days older than code",
                severity="low" if (code_mtime - doc_mtime).days < 30 else "medium"
            )

    def _parse_module(self, module_path: Path) -> Optional[ast.Module]:
        """
        Parse a Python module using AST.
        
        Args:
            module_path: Path to the module
            
        Returns:
            AST module or None if parsing failed
        """
        try:
            with open(module_path, "r", encoding="utf-8") as f:
                return ast.parse(f.read(), filename=str(module_path))
        except Exception as e:
            logger.error(f"Failed to parse {module_path}: {e}")
            return None
    
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """
        Get function signature from AST node.
        
        Args:
            node: Function definition node
            
        Returns:
            Function signature as string
        """
        args = []
        
        # Add positional args
        for arg in node.args.args:
            args.append(arg.arg)
            
        # Add vararg (*args)
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
            
        # Add keyword-only args
        for arg in node.args.kwonlyargs:
            args.append(arg.arg)
            
        # Add kwargs (**kwargs)
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")
            
        return ", ".join(args)
    
    def _get_function_params(self, node: ast.FunctionDef) -> List[str]:
        """
        Get function parameters from AST node.
        
        Args:
            node: Function definition node
            
        Returns:
            List of parameter names
        """
        params = []
        
        # Add positional args
        for arg in node.args.args:
            params.append(arg.arg)
            
        # Add vararg (*args)
        if node.args.vararg:
            params.append(node.args.vararg.arg)
            
        # Add keyword-only args
        for arg in node.args.kwonlyargs:
            params.append(arg.arg)
            
        # Add kwargs (**kwargs)
        if node.args.kwarg:
            params.append(node.args.kwarg.arg)
            
        return params
    
    def _signatures_match(self, code_sig: str, doc_sig: str) -> bool:
        """
        Check if code and doc signatures match.
        
        Args:
            code_sig: Code signature
            doc_sig: Documentation signature
            
        Returns:
            True if signatures match
        """
        # Normalize signatures for comparison
        def normalize(sig):
            sig = re.sub(r'\s+', '', sig)  # Remove whitespace
            sig = re.sub(r'[\'""]', '', sig)  # Remove quotes
            sig = re.sub(r'<.*?>', '', sig)  # Remove type hints
            sig = re.sub(r'\w+\s*=\s*[\w\.]+', lambda m: m.group(0).split('=')[0], sig)  # Keep param names, not defaults
            return sig
            
        return normalize(code_sig) == normalize(doc_sig)
    
    def _add_discrepancy(self, doc_path: Path, code_path: Path, element_name: str, 
                        discrepancy_type: str, description: str, severity: str) -> None:
        """
        Add a discrepancy to the list.
        
        Args:
            doc_path: Path to the documentation file
            code_path: Path to the code file
            element_name: Name of the affected element
            discrepancy_type: Type of discrepancy
            description: Description of the discrepancy
            severity: Severity level
        """
        discrepancy = DocDiscrepancy(
            doc_path=doc_path,
            code_path=code_path,
            element_name=element_name,
            discrepancy_type=discrepancy_type,
            description=description,
            severity=severity
        )
        self.discrepancies.append(discrepancy)
        logger.debug(f"📝 Found discrepancy: {discrepancy}")


def main() -> int:
    """Command-line interface for documentation validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate documentation against source code")
    parser.add_argument("--repo-root", type=Path, help="Repository root directory")
    parser.add_argument("--rules", nargs="+", help="Validation rules to apply")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()
    
    # Determine repository root
    repo_root = args.repo_root or Path(__file__).resolve().parent.parent
    
    # Create validator
    validator = DocValidator(repo_root)
    
    # Run validation
    discrepancies = validator.validate_all_documentation(args.rules)
    
    # Output results
    if args.json:
        import json
        result = {
            "discrepancies": [d.to_dict() for d in discrepancies],
            "count": len(discrepancies),
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"\n📊 Documentation Validation Results:")
        print(f"Found {len(discrepancies)} discrepancies")
        
        by_severity = {"high": [], "medium": [], "low": []}
        for d in discrepancies:
            by_severity[d.severity].append(d)
            
        if by_severity["high"]:
            print(f"\n🔴 HIGH SEVERITY ISSUES ({len(by_severity['high'])}):")
            for d in by_severity["high"]:
                print(f"  • {d}")
                
        if by_severity["medium"]:
            print(f"\n🟠 MEDIUM SEVERITY ISSUES ({len(by_severity['medium'])}):")
            for d in by_severity["medium"]:
                print(f"  • {d}")
                
        if by_severity["low"]:
            print(f"\n🟡 LOW SEVERITY ISSUES ({len(by_severity['low'])}):")
            for d in by_severity["low"]:
                print(f"  • {d}")
    
    return 0 if not discrepancies else 1


if __name__ == "__main__":
    sys.exit(main())
