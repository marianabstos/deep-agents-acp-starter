from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def _run_git(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None

    return result.stdout.strip() or None


def detect_package_manager(root: Path) -> str | None:
    markers = {
        "uv.lock": "uv",
        "poetry.lock": "poetry",
        "pdm.lock": "pdm",
        "package-lock.json": "npm",
        "pnpm-lock.yaml": "pnpm",
        "yarn.lock": "yarn",
        "bun.lockb": "bun",
        "Cargo.lock": "cargo",
    }

    for marker, manager in markers.items():
        if (root / marker).exists():
            return manager

    return None


def build_project_context() -> str:
    root = Path(os.environ.get("ACP_WORKSPACE_ROOT", os.getcwd())).resolve()
    git_root = _run_git(["rev-parse", "--show-toplevel"], root)
    branch = _run_git(["branch", "--show-current"], root)
    package_manager = detect_package_manager(root)

    tools = {
        "git": shutil.which("git") is not None,
        "uv": shutil.which("uv") is not None,
        "python": shutil.which("python") or shutil.which("python3"),
        "node": shutil.which("node") is not None,
    }

    lines = [
        "Current project context:",
        f"- Workspace root: {root}",
        f"- Git repository: {git_root or 'not detected'}",
        f"- Git branch: {branch or 'not detected'}",
        f"- Package manager: {package_manager or 'not detected'}",
        "- Available local tools:",
    ]

    for name, available in tools.items():
        lines.append(f"  - {name}: {'yes' if available else 'no'}")

    return "\n".join(lines)
