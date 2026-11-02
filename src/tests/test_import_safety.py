import os
from pathlib import Path
import subprocess
import sys


def test_package_import_does_not_load_cli_or_create_docs(tmp_path):
    source_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(source_root)
    code = """
import importlib.abc
import sys

class Guard(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in {'doc_forge.run', 'doc_forge.doc_forge'}:
            raise RuntimeError('CLI imported during package import')
        return None

sys.meta_path.insert(0, Guard())
import doc_forge
assert callable(doc_forge.run_cli)
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "docs").exists()


def test_docs_path_can_be_resolved_without_creating_it(tmp_path, monkeypatch):
    from doc_forge.utils import paths

    monkeypatch.setattr(paths, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(paths, "_DOCS_DIR", None)
    assert paths.get_docs_dir(create=False) == tmp_path / "docs"
    assert not (tmp_path / "docs").exists()
    assert paths.get_docs_dir() == tmp_path / "docs"
    assert (tmp_path / "docs").is_dir()


def test_cli_help_does_not_create_docs(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    code = """
from pathlib import Path
import sys
from doc_forge.utils import paths
paths._REPO_ROOT = Path.cwd()
paths._DOCS_DIR = None
sys.argv = ['doc-forge', '--help']
from doc_forge.doc_forge import main
main()
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "docs").exists()
