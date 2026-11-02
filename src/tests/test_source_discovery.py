from pathlib import Path

import pytest

from doc_forge.source_discovery import DocumentationDiscovery


@pytest.fixture
def discovery(tmp_path, monkeypatch):
    # An underscore in an ancestor outside the docs tree is not a private doc.
    repo = tmp_path / "_workspace"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    structure = {
        "user_docs": docs / "user_docs",
        "auto_docs": docs / "auto_docs",
        "ai_docs": docs / "ai_docs",
    }
    monkeypatch.setattr(
        "doc_forge.source_discovery.get_doc_structure", lambda _: structure
    )
    return DocumentationDiscovery(repo_root=repo, docs_dir=docs), structure


def write_doc(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("Example document", encoding="utf-8")
    return path


def test_find_all_sources_empty_directories(discovery):
    finder, _ = discovery
    orphan = finder.docs_dir / "orphaned.md"
    finder.orphaned_documents = [orphan]

    assert finder.find_all_sources() == {
        "user": [], "auto": [], "ai": [], "orphaned": [orphan]
    }


def test_find_all_sources_with_content(discovery):
    finder, paths = discovery
    user = {
        write_doc(paths["user_docs"] / "guide.md"),
        write_doc(paths["user_docs"] / "guide.rst"),
    }
    auto = {
        write_doc(paths["auto_docs"] / "api" / "module.md"),
        write_doc(finder.docs_dir / "reference" / "class.rst"),
        write_doc(finder.docs_dir / "autoapi" / "api.txt"),
        write_doc(finder.docs_dir / "apidoc" / "index.md"),
    }
    ai = {write_doc(paths["ai_docs"] / "concept.md")}
    write_doc(paths["user_docs"] / "_private" / "hidden.md")
    write_doc(paths["ai_docs"] / "_drafts" / "draft.md")
    write_doc(paths["auto_docs"] / "_private.md")
    write_doc(paths["user_docs"] / "ignored.pdf")

    result = finder.find_all_sources()

    assert set(result["user"]) == user
    assert set(result["auto"]) == auto
    assert set(result["ai"]) == ai
    assert result["orphaned"] == []


def test_find_all_sources_only_user_docs(discovery):
    finder, paths = discovery
    user = {
        write_doc(paths["user_docs"] / "guide.md"),
        write_doc(paths["user_docs"] / "guide.rst"),
    }
    orphan = finder.docs_dir / "orphaned.md"
    finder.orphaned_documents = [orphan]

    result = finder.find_all_sources()

    assert set(result["user"]) == user
    assert result["auto"] == []
    assert result["ai"] == []
    assert result["orphaned"] == [orphan]


def test_find_all_sources_integration(discovery):
    finder, paths = discovery
    user = write_doc(paths["user_docs"] / "guide.md")
    auto = write_doc(paths["auto_docs"] / "api.rst")
    ai = write_doc(paths["ai_docs"] / "concept.md")
    orphan = write_doc(finder.docs_dir / "orphaned.md")
    write_doc(paths["user_docs"] / "_private" / "draft.md")
    finder.orphaned_documents = [orphan]

    result = finder.find_all_sources()

    assert result == {
        "user": [user],
        "auto": [auto],
        "ai": [ai],
        "orphaned": [orphan],
    }
