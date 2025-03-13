from pathlib import Path
from doc_forge.source_discovery import discover_code_structures

def generate_todo_document():
    repo_root = Path(__file__).resolve().parents[1]
    items = discover_code_structures(repo_root / "src")
    todo_path = repo_root / "tests" / "doc_forge_todo.md"
    with open(todo_path, "w", encoding="utf-8") as f:
        f.write("# Doc Forge Comprehensive TODO\n\n")
        for item in items:
            f.write(f"- [{item['type'].title()}] {item['name']} ({item['file']})\n")
    return todo_path

if __name__ == "__main__":
    generated_file = generate_todo_document()
    print(f"Generated testing TODO document at: {generated_file}")
