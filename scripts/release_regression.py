#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STARTUP_ENTRYPOINTS_TEST = "tests/integration/test_startup_entrypoints.py"


@dataclass(frozen=True)
class RegressionCommand:
    name: str
    command: tuple[str, ...]
    env: dict[str, str] | None = None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run VocabChan release regression checks before packaging."
    )
    parser.add_argument(
        "--only",
        nargs="*",
        metavar="CHECK",
        help="Run only the named checks. Defaults to the full release suite.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print the available checks and exit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved commands without running them.",
    )
    return parser.parse_args(argv)


def build_commands() -> list[RegressionCommand]:
    startup_env = {
        "QT_QPA_PLATFORM": "offscreen",
        "VOCABCHAN_STARTUP_SMOKE": "1",
        "PYTHONPATH": str(PROJECT_ROOT / "src"),
    }
    commands = [
        RegressionCommand("unit", (sys.executable, "-m", "pytest", "tests/unit", "-q")),
        RegressionCommand(
            "integration",
            (
                sys.executable,
                "-m",
                "pytest",
                "tests/integration",
                "-q",
                f"--ignore={STARTUP_ENTRYPOINTS_TEST}",
            ),
        ),
        RegressionCommand("imports", (sys.executable, "bin/smoke_imports.py")),
        RegressionCommand(
            "startup-main",
            (sys.executable, "main.py"),
            env=startup_env,
        ),
        RegressionCommand(
            "startup-module",
            (sys.executable, "-m", "vocabchan"),
            env=startup_env,
        ),
        RegressionCommand(
            "package-dry-run",
            (sys.executable, "scripts/package_release.py", "--dry-run"),
        ),
    ]
    if os.name == "nt":
        commands.append(
            RegressionCommand(
                "build-bat-dry-run",
                ("cmd", "/c", "build.bat", "--dry-run"),
            )
        )
    return commands


def select_commands(all_commands: list[RegressionCommand], names: list[str] | None) -> list[RegressionCommand]:
    if not names:
        return all_commands
    wanted = set(names)
    selected = [command for command in all_commands if command.name in wanted]
    missing = wanted - {command.name for command in selected}
    if missing:
        raise ValueError(f"Unknown checks: {', '.join(sorted(missing))}")
    return selected


def run_command(command: RegressionCommand, *, dry_run: bool) -> int:
    rendered = shlex.join(command.command)
    print(f"[{command.name}] {rendered}", flush=True)
    if dry_run:
        return 0
    env = os.environ.copy()
    if command.env:
        env.update(command.env)
    completed = subprocess.run(
        list(command.command),
        cwd=PROJECT_ROOT,
        env=env,
        check=False,
    )
    return int(completed.returncode)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    commands = build_commands()
    if args.list:
        for command in commands:
            print(command.name)
        return 0

    try:
        selected = select_commands(commands, args.only)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    for command in selected:
        exit_code = run_command(command, dry_run=args.dry_run)
        if exit_code != 0:
            print(
                f"[FAILED] {command.name} exited with code {exit_code}",
                file=sys.stderr,
                flush=True,
            )
            return exit_code
    print("[DONE] Release regression suite finished.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
