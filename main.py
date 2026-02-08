from __future__ import annotations

import sys
import termios
import tty
from typing import List, Optional

from rich.console import Console
from rich.live import Live
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from modules.dungeon_master import enter_dungeon
from modules.gate_scanner import scan_subjects

CONSOLE = Console()


def build_dungeon_table(dungeons: List[dict], selected_index: int) -> Table:
    table = Table(title="SOLO LEVELING // DUNGEON LIST", header_style="bold cyan")
    table.add_column("ID", style="cyan", justify="right", width=4)
    table.add_column("Rank/Exam", style="bright_magenta")
    table.add_column("Name", style="white")
    table.add_column("Status", style="bright_green")

    if not dungeons:
        table.add_row("-", "-", "No dungeons discovered", "-")
        return table

    for idx, dungeon in enumerate(dungeons, start=1):
        status = "Ready" if dungeon["has_tester"] else "Missing tester"
        row_style = "bold yellow" if idx - 1 == selected_index else ""
        table.add_row(
            str(idx),
            str(dungeon["level"]),
            str(dungeon["name"]),
            status,
            style=row_style,
        )
    return table


def _read_key() -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        first = sys.stdin.read(1)
        if first == "\x1b":
            second = sys.stdin.read(1)
            third = sys.stdin.read(1)
            return first + second + third
        return first
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def select_dungeon(dungeons: List[dict]) -> Optional[dict]:
    if not dungeons:
        return None

    if not sys.stdin.isatty():
        choice = Prompt.ask("Select dungeon by ID", default="1")
        if not choice.isdigit():
            return None
        index = int(choice) - 1
        if 0 <= index < len(dungeons):
            return dungeons[index]
        return None

    index = 0
    CONSOLE.print(Text("Use ↑/↓ to move, Enter to select, or type an ID.", style="bright_cyan"))

    with Live(build_dungeon_table(dungeons, index), console=CONSOLE, refresh_per_second=10) as live:
        while True:
            key = _read_key()
            if key in {"\x1b[A", "k"}:
                index = (index - 1) % len(dungeons)
            elif key in {"\x1b[B", "j"}:
                index = (index + 1) % len(dungeons)
            elif key == "\r":
                return dungeons[index]
            elif key.isdigit():
                digit_index = int(key) - 1
                if 0 <= digit_index < len(dungeons):
                    return dungeons[digit_index]
            elif key in {"q", "Q"}:
                return None
            live.update(build_dungeon_table(dungeons, index))


def main() -> None:
    dungeons = scan_subjects()
    selected = select_dungeon(dungeons)
    if not selected:
        CONSOLE.print("[bold red]No dungeon selected. Exiting.[/]")
        return
    exit_code = enter_dungeon(selected["path"])
    if exit_code == 0:
        CONSOLE.print("[bold green]Dungeon clear![/]")
    else:
        CONSOLE.print("[bold red]Dungeon failed. Check the output above.[/]")


if __name__ == "__main__":
    main()
