from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

CONSOLE = Console()
WORKSPACE_DIR = Path("current_dungeon")


def _reset_workspace() -> None:
    if WORKSPACE_DIR.exists():
        shutil.rmtree(WORKSPACE_DIR)
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)


def _copy_exercise_contents(source: Path) -> None:
    for item in source.iterdir():
        destination = WORKSPACE_DIR / item.name
        if item.is_dir():
            shutil.copytree(item, destination)
        else:
            shutil.copy2(item, destination)


def enter_dungeon(exercise_path: str | Path) -> int:
    source = Path(exercise_path)
    if not source.exists():
        CONSOLE.print("[bold red]Exercise path not found.[/]")
        return 1

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]INITIALIZING DUNGEON..."),
        console=CONSOLE,
    ) as progress:
        progress.add_task("init", total=None)
        _reset_workspace()
        _copy_exercise_contents(source)

    CONSOLE.print(
        "[bold green]Dungeon ready![/] Write your code in ./current_dungeon/ and press Enter to Grade."
    )
    input()

    tester_path = WORKSPACE_DIR / "tester.sh"
    if not tester_path.exists():
        CONSOLE.print("[bold red]tester.sh not found in the dungeon workspace.[/]")
        return 1

    tester_path.chmod(tester_path.stat().st_mode | 0o111)
    result = subprocess.run(
        ["bash", str(tester_path)],
        cwd=WORKSPACE_DIR,
        text=True,
        capture_output=True,
    )
    if result.stdout:
        CONSOLE.print(result.stdout)
    if result.stderr:
        CONSOLE.print(result.stderr)
    return result.returncode
