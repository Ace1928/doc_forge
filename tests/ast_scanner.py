from pathlib import Path
import re
import sys
import ast
import importlib
import inspect
from typing import Dict, List, Set, Tuple, Optional, Any, Counter
from doc_forge.source_discovery import discover_code_structures

class CodeEntityAnalyzer:
    """
    Advanced code entity analyzer with comprehensive inspection capabilities.
    Discovers and categorizes code structures with Eidosian precision.
    """
    
    def __init__(self, repo_root: Path):
        """Initialize the analyzer with repository root."""
        self.repo_root = repo_root
        self.src_dir = repo_root / "src"
        self.tests_dir = repo_root / "tests"
        self.discovered_items = []
        self.test_functions = set()
        self.module_structure = {}
    
    def discover_all_structures(self) -> List[Dict[str, Any]]:
        """
        Comprehensively analyze the codebase and discover all code structures.
        Return enriched structure information including parameters, return types, etc.
        """
        # First get the basic structures
        raw_items = discover_code_structures(self.src_dir)
        
        # Enhance items with additional information
        enriched_items = []
        for item in raw_items:
            # Add module path for better categorization
            file_path = Path(item["file"])
            rel_path = file_path.relative_to(self.repo_root)
            module_path = ".".join(rel_path.with_suffix("").parts[1:])
            
            enriched_item = {
                **item,
                "module_path": module_path,
                "parameters": [],
                "has_docstring": False,
                "return_type": None,
                "complexity": self._estimate_complexity(file_path, item["name"], item["type"])
            }
            
            # Try to extract more detailed information
            try:
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if ((item["type"] == "function" and isinstance(node, ast.FunctionDef) or
                             item["type"] == "class" and isinstance(node, ast.ClassDef)) and
                            node.name == item["name"]):
                            
                            # Check for docstring
                            if (node.body and isinstance(node.body[0], ast.Expr) and
                                isinstance(node.body[0].value, ast.Str)):
                                enriched_item["has_docstring"] = True
                            
                            # For functions, get parameters and return type hint
                            if isinstance(node, ast.FunctionDef):
                                enriched_item["parameters"] = [arg.arg for arg in node.args.args 
                                                             if arg.arg != 'self' and arg.arg != 'cls']
                                
                                # Try to get return type annotation
                                if node.returns:
                                    enriched_item["return_type"] = ast.unparse(node.returns)
            except Exception as e:
                pass  # Skip if any issues with detailed analysis
                
            enriched_items.append(enriched_item)
            
        self.discovered_items = enriched_items
        return enriched_items
    
    def analyze_tests(self) -> Dict[str, Any]:
        """
        Analyze existing test files to determine current test coverage
        and create a mapping from code entities to tests.
        """
        self.test_functions = set()
        test_files = {}
        
        # Find all test files
        for test_file in self.tests_dir.glob("test_*.py"):
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Get all test functions
            matches = re.findall(r'def\s+(test_[^\s\(]+)', content)
            
            # Track test file and its functions
            test_files[test_file.stem] = {
                "path": test_file,
                "functions": matches,
                "content": content
            }
            
            # Add to global test function set
            for match in matches:
                self.test_functions.add(match.lower())
        
        # Cross-reference items with test functions
        coverage_data = self._analyze_coverage()
        
        return {
            "test_files": test_files,
            "coverage": coverage_data,
            "total_items": len(self.discovered_items),
            "tested_items": len(coverage_data["tested"]),
            "untested_items": len(coverage_data["untested"]),
            "coverage_percentage": self._calculate_coverage_percentage(coverage_data)
        }
    
    def _analyze_coverage(self) -> Dict[str, List]:
        """Determine which items are tested and which are not."""
        tested = []
        untested = []
        
        # Group by module for hierarchical analysis
        by_module = {}
        
        for item in self.discovered_items:
            # Check both direct name match and module.name match
            module_parts = item["module_path"].split(".")
            item_name = item["name"].lower()
            test_patterns = [
                f"test_{item_name}",
                f"test_{module_parts[-1]}_{item_name}" if module_parts else f"test_{item_name}"
            ]
            
            # For classes, also check for test_ClassNameMethod patterns
            if item["type"] == "class":
                test_patterns.append(f"test_{item_name}_")  # Class method tests often start with this
            
            is_tested = any(any(pattern in fn for fn in self.test_functions) 
                           for pattern in test_patterns)
            
            # Add module info to grouping
            module_name = ".".join(module_parts[:-1]) if len(module_parts) > 1 else "root"
            if module_name not in by_module:
                by_module[module_name] = {"tested": [], "untested": []}
                
            if is_tested:
                tested.append(item)
                by_module[module_name]["tested"].append(item)
            else:
                untested.append(item)
                by_module[module_name]["untested"].append(item)
        
        # Sort items alphabetically by name for consistent output
        tested.sort(key=lambda x: x["name"])
        untested.sort(key=lambda x: x["name"])
        
        self.module_structure = by_module
        
        return {"tested": tested, "untested": untested, "by_module": by_module}
    
    def _calculate_coverage_percentage(self, coverage_data: Dict) -> float:
        """Calculate test coverage percentage."""
        total = len(coverage_data["tested"]) + len(coverage_data["untested"])
        if total == 0:
            return 100.0  # Nothing to test means full coverage
        return (len(coverage_data["tested"]) / total) * 100
    
    def _estimate_complexity(self, file_path: Path, name: str, item_type: str) -> int:
        """Estimate item complexity to prioritize tests."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            tree = ast.parse(content)
            complexity = 1  # Base complexity
            
            for node in ast.walk(tree):
                if ((item_type == "function" and isinstance(node, ast.FunctionDef) or
                     item_type == "class" and isinstance(node, ast.ClassDef)) and
                    node.name == name):
                    
                    # Count branches (if/else statements)
                    branch_count = sum(1 for _ in ast.walk(node) if isinstance(_, (ast.If, ast.For, ast.While)))
                    
                    # Count function calls
                    call_count = sum(1 for _ in ast.walk(node) if isinstance(_, ast.Call))
                    
                    # Count returns
                    return_count = sum(1 for _ in ast.walk(node) if isinstance(_, ast.Return))
                    
                    complexity = 1 + branch_count + (call_count // 5) + (return_count // 2)
                    
                    # Classes are typically more complex
                    if item_type == "class":
                        complexity += 2
                        
                    # Check for specific keywords that suggest complexity
                    source = ast.unparse(node)
                    if "except" in source:
                        complexity += 2
                    if "async" in source:
                        complexity += 1
                        
                    break
                    
            return complexity
        except Exception:
            return 1  # Default complexity if analysis fails
    
    def generate_test_suggestions(self) -> Dict[str, Any]:
        """
        Generate test suggestions based on code analysis.
        Returns a dictionary with priorities and suggested test approaches.
        """
        if not self.discovered_items:
            self.discover_all_structures()
            
        coverage = self._analyze_coverage()
        untested = coverage["untested"]
        
        # Prioritize untested items by complexity and type
        prioritized = sorted(untested, key=lambda x: (
            -x.get("complexity", 1),  # Higher complexity first
            2 if x["type"] == "class" else 1,  # Classes over functions
            0 if x.get("has_docstring", False) else 1,  # Items with docs are slightly easier to test
            x["name"]  # Alphabetical for consistency
        ))
        
        # Generate suggestions for each untested item
        suggestions = []
        for item in prioritized:
            suggestion = {
                "item": item,
                "priority": "high" if item.get("complexity", 1) > 5 else "medium" if item.get("complexity", 1) > 2 else "low",
                "suggested_approach": self._suggest_test_approach(item),
                "test_function_name": f"test_{item['name'].lower()}",
            }
            suggestions.append(suggestion)
            
        return {
            "suggestions": suggestions,
            "by_priority": {
                "high": [s for s in suggestions if s["priority"] == "high"],
                "medium": [s for s in suggestions if s["priority"] == "medium"],
                "low": [s for s in suggestions if s["priority"] == "low"]
            }
        }
    
    def _suggest_test_approach(self, item: Dict[str, Any]) -> str:
        """Suggest test approach based on item type and properties."""
        if item["type"] == "class":
            return f"Create a test class `Test{item['name']}` with setup/teardown methods and test each public method."
        elif "parameters" in item and item["parameters"]:
            param_text = ", ".join(item["parameters"])
            return f"Test with various input combinations for parameters: {param_text}."
        else:
            return f"Create a simple function test that verifies expected behavior."

    def generate_test_stubs(self, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Generate test stub files for untested items.
        Returns information about generated stubs.
        """
        if not output_dir:
            output_dir = self.tests_dir
            
        if not self.discovered_items:
            self.discover_all_structures()
            
        coverage = self._analyze_coverage()
        untested = coverage["untested"]
        
        # Group by module for better organization
        by_module = {}
        for item in untested:
            module_parts = item["module_path"].split(".")
            module_name = module_parts[0] if module_parts else "core"
            
            if module_name not in by_module:
                by_module[module_name] = []
                
            by_module[module_name].append(item)
        
        # Generate stub files for each module
        generated_files = []
        for module_name, items in by_module.items():
            if not items:
                continue
                
            stub_file = output_dir / f"test_{module_name}_stubs.py"
            
            with open(stub_file, "w", encoding="utf-8") as f:
                # Write imports
                f.write("import unittest\n")
                f.write("import pytest\n")
                
                # Import the module
                f.write(f"import {module_name}\n\n")
                
                # Write test stubs for each item
                for item in items:
                    if item["type"] == "class":
                        f.write(f"class Test{item['name']}(unittest.TestCase):\n")
                        f.write(f"    \"\"\"Tests for {item['name']} class.\"\"\"\n\n")
                        f.write("    def setUp(self):\n")
                        f.write("        # Setup code here\n")
                        f.write("        pass\n\n")
                        f.write(f"    def test_{item['name'].lower()}_initialization(self):\n")
                        f.write(f"        # Test {item['name']} initialization\n")
                        f.write("        self.assertTrue(True)  # Replace with actual test\n\n")
                    else:  # Function
                        f.write(f"def test_{item['name'].lower()}():\n")
                        f.write(f"    \"\"\"Test {item['name']} function.\"\"\"\n")
                        f.write("    # Test implementation here\n")
                        f.write("    assert True  # Replace with actual test\n\n")
                        
            generated_files.append(str(stub_file))
                
        return {
            "generated_files": generated_files,
            "stub_count": len(generated_files),
            "covered_items": sum(len(items) for items in by_module.values())
        }

def generate_todo_document():
    """Generate a comprehensive TODO document for all code structures."""
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = CodeEntityAnalyzer(repo_root)
    items = analyzer.discover_all_structures()
    
    todo_path = repo_root / "tests" / "doc_forge_todo.md"
    with open(todo_path, "w", encoding="utf-8") as f:
        f.write("# Doc Forge Comprehensive Test TODO\n\n")
        f.write("This document outlines all testable code structures and their current test status.\n\n")
        
        # Group by module
        by_module = {}
        for item in items:
            module_path = item.get("module_path", "unknown")
            if module_path not in by_module:
                by_module[module_path] = []
            by_module[module_path].append(item)
        
        # Write by module
        for module, module_items in sorted(by_module.items()):
            f.write(f"## Module: `{module}`\n\n")
            
            # List classes first, then functions
            classes = [i for i in module_items if i["type"] == "class"]
            functions = [i for i in module_items if i["type"] == "function"]
            
            if classes:
                f.write("### Classes\n\n")
                for item in sorted(classes, key=lambda x: x["name"]):
                    params = ", ".join(item.get("parameters", []))
                    has_doc = "✅" if item.get("has_docstring", False) else "❌"
                    f.write(f"- [{item['type'].title()}] **{item['name']}** ({params}) | Docstring: {has_doc} | Complexity: {item.get('complexity', 1)}\n")
            
            if functions:
                f.write("\n### Functions\n\n")
                for item in sorted(functions, key=lambda x: x["name"]):
                    params = ", ".join(item.get("parameters", []))
                    has_doc = "✅" if item.get("has_docstring", False) else "❌"
                    f.write(f"- [{item['type'].title()}] **{item['name']}** ({params}) | Docstring: {has_doc} | Complexity: {item.get('complexity', 1)}\n")
                    
            f.write("\n")
            
    return todo_path

def generate_coverage_report():
    """
    Generate a comprehensive coverage report with module-level analysis
    and test suggestions.
    """
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = CodeEntityAnalyzer(repo_root)
    analyzer.discover_all_structures()
    test_analysis = analyzer.analyze_tests()
    suggestions = analyzer.generate_test_suggestions()
    
    coverage_path = repo_root / "tests" / "doc_forge_coverage.md"
    with open(coverage_path, "w", encoding="utf-8") as f:
        f.write("# Doc Forge Test Coverage Report\n\n")
        
        # Write summary statistics
        coverage_pct = test_analysis["coverage_percentage"]
        f.write(f"## Coverage Summary\n\n")
        f.write(f"- **Overall Coverage**: {coverage_pct:.1f}%\n")
        f.write(f"- **Total Items**: {test_analysis['total_items']}\n")
        f.write(f"- **Tested Items**: {test_analysis['tested_items']}\n")
        f.write(f"- **Untested Items**: {test_analysis['untested_items']}\n\n")
        
        # Write module-level coverage
        f.write("## Coverage by Module\n\n")
        for module_name, data in test_analysis["coverage"]["by_module"].items():
            total = len(data["tested"]) + len(data["untested"])
            if total == 0:
                continue
                
            module_pct = (len(data["tested"]) / total) * 100
            f.write(f"### {module_name}\n\n")
            f.write(f"- Coverage: {module_pct:.1f}%\n")
            f.write(f"- Tested: {len(data['tested'])}\n")
            f.write(f"- Untested: {len(data['untested'])}\n\n")
        
        # Write tested items
        f.write("## Tested Items\n\n")
        for item in test_analysis["coverage"]["tested"]:
            f.write(f"- **{item['type'].title()}**: `{item['name']}` ({item['module_path']})\n")
        
        # Write untested items with priority
        f.write("\n## Untested Items\n\n")
        
        # Group by priority
        for priority in ["high", "medium", "low"]:
            priority_items = [s for s in suggestions["suggestions"] if s["priority"] == priority]
            if priority_items:
                f.write(f"### {priority.title()} Priority\n\n")
                for suggestion in priority_items:
                    item = suggestion["item"]
                    f.write(f"- **{item['type'].title()}**: `{item['name']}` ({item['module_path']})\n")
                    f.write(f"  - **Suggestion**: {suggestion['suggested_approach']}\n")
                    f.write(f"  - **Proposed Test Name**: `{suggestion['test_function_name']}`\n\n")
        
    return coverage_path

def generate_test_stubs():
    """Generate test stub files for untested items."""
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = CodeEntityAnalyzer(repo_root)
    analyzer.discover_all_structures()
    analyzer.analyze_tests()
    
    # Generate stubs
    stubs_info = analyzer.generate_test_stubs()
    
    print(f"✅ Generated {stubs_info['stub_count']} test stub files:")
    for file_path in stubs_info["generated_files"]:
        print(f"  - {file_path}")
    
    return stubs_info["generated_files"]

if __name__ == "__main__":
    # Process command-line arguments
    if "--todo" in sys.argv or len(sys.argv) == 1:
        todo_file = generate_todo_document()
        print(f"✅ Generated test TODO document at: {todo_file}")
        
    if "--coverage" in sys.argv or len(sys.argv) == 1:
        coverage_file = generate_coverage_report()
        print(f"✅ Coverage report created at: {coverage_file}")
        
    if "--stubs" in sys.argv:
        stub_files = generate_test_stubs()
        
    if "--help" in sys.argv:
        print("Available options:")
        print("  --todo      Generate comprehensive TODO document")
        print("  --coverage  Generate test coverage report")
        print("  --stubs     Generate test stub files")
        print("  --help      Show this help message")
