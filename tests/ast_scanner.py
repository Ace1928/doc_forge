from pathlib import Path
from doc_forge.source_discovery import discover_code_structures
import re
import sys

def generate_todo_document():
    repo_root = Path(__file__).resolve().parents[1]
    items = discover_code_structures(repo_root / "src")
    todo_path = repo_root / "tests" / "doc_forge_todo.md"
    with open(todo_path, "w", encoding="utf-8") as f:
        f.write("# Doc Forge Comprehensive TODO\n\n")
        for item in items:
            f.write(f"- [{item['type'].title()}] {item['name']} ({item['file']})\n")
    return todo_path

def check_test_coverage(discovered_items):
    """
    Scan all test_*.py files for functions that match discovered items.
    Return a dict with 'tested' and 'untested' items.
    """
    tests_path = Path(__file__).resolve().parent
    test_functions = set()
    for test_file in tests_path.glob("test_*.py"):
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
        # Roughly match 'def test_something' lines
        matches = re.findall(r'def\s+(test_[^\s\(]+)', content)
        for m in matches:
            test_functions.add(m.lower())
    tested = []
    untested = []
    for item in discovered_items:
        item_name = f"test_{item['name'].lower()}"
        if any(item_name in fn for fn in test_functions):
            tested.append(item)
        else:
            untested.append(item)
    return {"tested": tested, "untested": untested}

def generate_coverage_report():
    """
    Cross-reference discovered code items with found test functions
    and write a coverage report to doc_forge_coverage.md.
    """
    repo_root = Path(__file__).resolve().parents[1]
    items = discover_code_structures(repo_root / "src")
    coverage = check_test_coverage(items)
    coverage_path = repo_root / "tests" / "doc_forge_coverage.md"
    with open(coverage_path, "w", encoding="utf-8") as f:
        f.write("# Doc Forge Coverage Report\n\n")
        f.write("## Tested Items\n")
        for t in coverage["tested"]:
            f.write(f"- {t['type']} {t['name']} ({t['file']})\n")
        f.write("\n## Untested Items\n")
        for u in coverage["untested"]:
            f.write(f"- {u['type']} {u['name']} ({u['file']})\n")
    return coverage_path

if __name__ == "__main__":
    generated_file = generate_todo_document()
    print(f"Generated testing TODO document at: {generated_file}")
    if "--coverage" in sys.argv:
        coverage_file = generate_coverage_report()
        print(f"Coverage report created at: {coverage_file}")
