#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a VocabChan desktop release via PyInstaller.")
    parser.add_argument("--dry-run", action="store_true", help="Print the resolved PyInstaller command and exit.")
    parser.add_argument("--dist-dir", default="dist", help="Output directory for the packaged app.")
    parser.add_argument("--work-dir", default="build/pyinstaller", help="Working directory for PyInstaller artifacts.")
    parser.add_argument("--name", default="VocabChan", help="Application name used by PyInstaller.")
    parser.add_argument("--clean", action=argparse.BooleanOptionalAction, default=True, help="Clear PyInstaller caches before building.")
    return parser.parse_args(argv)


def load_project_version(pyproject_path: Path | None = None) -> str:
    config_path = pyproject_path or PROJECT_ROOT / "pyproject.toml"
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def build_pyinstaller_command(
    *,
    app_name: str,
    dist_dir: Path,
    work_dir: Path,
    clean: bool,
) -> list[str]:
    separator = ";" if os.name == "nt" else ":"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--windowed",
        "--name",
        app_name,
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(work_dir),
        "--specpath",
        str(work_dir),
        "--paths",
        str(PROJECT_ROOT / "src"),
        "--add-data",
        f"{PROJECT_ROOT / 'resources'}{separator}resources",
        "--add-data",
        f"{PROJECT_ROOT / 'README.md'}{separator}.",
        str(PROJECT_ROOT / "main.py"),
    ]
    if clean:
        command.insert(3, "--clean")
    return command


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    dist_dir = (PROJECT_ROOT / args.dist_dir).resolve()
    work_dir = (PROJECT_ROOT / args.work_dir).resolve()
    version = load_project_version()
    command = build_pyinstaller_command(
        app_name=args.name,
        dist_dir=dist_dir,
        work_dir=work_dir,
        clean=args.clean,
    )

    if args.dry_run:
        print(f"VocabChan {version}")
        print(shlex.join(command))
        return 0

    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller is not installed. Run: pip install -e \".[package]\"", file=sys.stderr)
        return 1

    dist_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
