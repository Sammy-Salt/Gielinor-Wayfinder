from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

def test_governance_files_and_git_exist():
    required = [
        "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md", ".github/copilot-instructions.md",
        "docs/development/AI_CHANGE_PROTOCOL.md", "docs/development/PROJECT_ANALYSIS.md",
        "docs/releases/PASS31.26.md", ".githooks/pre-commit", "scripts/setup-git-hooks.sh",
        "scripts/verify_project.py", ".git/HEAD",
    ]
    for rel in required:
        assert (ROOT / rel).exists(), rel

def test_release_metadata_is_synchronized():
    rel = json.loads((SITE / "release.json").read_text())
    root = json.loads((ROOT / "release-manifest.json").read_text())
    site = json.loads((SITE / "release-manifest.json").read_text())
    assert rel["release"] == "PASS31.51"
    assert rel["buildId"] == "pass31.51-20261108-1"
    assert root["release"] == rel["release"] and root["buildId"] == rel["buildId"]
    assert site["release"] == rel["release"] and site["buildId"] == rel["buildId"]

def test_generated_caches_are_not_tracked():
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    assert not any("__pycache__/" in path or path.endswith(".pyc") or ".pytest_cache/" in path for path in tracked)
    assert "__pycache__/" in (ROOT / ".gitignore").read_text()
    assert ".pytest_cache/" in (ROOT / ".gitignore").read_text()

def test_project_verifier_passes():
    result = subprocess.run(["python3", "scripts/verify_project.py"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
