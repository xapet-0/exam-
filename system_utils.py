import json
import subprocess
import time
from pathlib import Path
from typing import Dict

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

CONSOLE = Console()
DAILY_STATE_PATH = Path("data/daily_state.json")
PENALTY_COMMAND = "./exercises/penalty_quest"


def calculate_level(xp: int) -> Dict[str, int]:
    level = max(1, xp // 500 + 1)
    next_level_xp = level * 500
    return {"level": level, "next_level_xp": next_level_xp}


def run_command(command: str) -> int:
    if not command:
        CONSOLE.print("[bold red]No command configured for this gate.[/]")
        return 1
    CONSOLE.print(Panel(f"Executing: {command}", border_style="bright_cyan"))
    return subprocess.call(command, shell=True)


def play_level_up_animation(level: int) -> None:
    art = Text(
        f"""
 ██████╗ ██╗   ██╗███████╗███████╗███████╗██╗     ██╗
██╔═══██╗██║   ██║██╔════╝██╔════╝██╔════╝██║     ██║
██║   ██║██║   ██║███████╗█████╗  █████╗  ██║     ██║
██║   ██║██║   ██║╚════██║██╔══╝  ██╔══╝  ██║     ██║
╚██████╔╝╚██████╔╝███████║███████╗██║     ███████╗███████╗
 ╚═════╝  ╚═════╝ ╚══════╝╚══════╝╚═╝     ╚══════╝╚══════╝

                LEVEL {level} UNLOCKED
""",
        style="bright_cyan",
    )
    CONSOLE.clear()
    CONSOLE.print(Panel(art, border_style="bright_magenta"))
    time.sleep(1.2)


def load_daily_state() -> Dict[str, object]:
    if DAILY_STATE_PATH.exists():
        return json.loads(DAILY_STATE_PATH.read_text(encoding="utf-8"))
    return {"date": None, "quests": []}


def save_daily_state(state: Dict[str, object]) -> None:
    DAILY_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    DAILY_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def run_penalty_quest() -> None:
    if Path(PENALTY_COMMAND).exists():
        run_command(PENALTY_COMMAND)
        return
    CONSOLE.print(
        Panel(
            "Penalty quest binary not found. Add ./exercises/penalty_quest to enforce this gate.",
            border_style="bright_magenta",
        )
    )
