from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent


PROJECT_ROOT = Path(__file__).resolve().parent


def ensure_rich() -> None:
    if _has_rich():
        return
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "rich"],
        check=False,
    )


def _has_rich() -> bool:
    import importlib.util

    return importlib.util.find_spec("rich") is not None


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_settings() -> dict:
    return {
        "player_name": "Jin-Woo",
        "rank": "E",
        "xp": 0,
        "gold": 0,
        "fatigue": 0,
        "system_version": "v1.0",
    }


def build_hunter_py() -> str:
    return dedent(
        """
        from __future__ import annotations

        from dataclasses import dataclass, field


        RANKS = ["E", "D", "C", "B", "A", "S"]


        @dataclass
        class Hunter:
            name: str
            rank: str = "E"
            xp: int = 0
            gold: int = 0
            fatigue: int = 0
            xp_thresholds: dict = field(
                default_factory=lambda: {"E": 100, "D": 250, "C": 500, "B": 900, "A": 1400}
            )

            def gain_xp(self, amount: int) -> None:
                self.xp += max(0, amount)
                self._check_level_up()

            def gain_gold(self, amount: int) -> None:
                self.gold += max(0, amount)

            def add_fatigue(self, amount: int) -> None:
                self.fatigue = max(0, self.fatigue + amount)

            def _check_level_up(self) -> None:
                while self.rank in self.xp_thresholds and self.xp >= self.xp_thresholds[self.rank]:
                    current_index = RANKS.index(self.rank)
                    if current_index + 1 >= len(RANKS):
                        break
                    self.rank = RANKS[current_index + 1]
                    self.fatigue = 0

            def summary(self) -> dict:
                return {
                    "name": self.name,
                    "rank": self.rank,
                    "xp": self.xp,
                    "gold": self.gold,
                    "fatigue": self.fatigue,
                }
        """
    ).lstrip()


def build_gate_loader_py() -> str:
    return dedent(
        """
        from __future__ import annotations

        from pathlib import Path
        from typing import Dict, List


        def _rank_from_exam(exam_name: str) -> str:
            try:
                exam_number = int(exam_name.replace("exam_", ""))
            except ValueError:
                return "E"
            if exam_number <= 1:
                return "E"
            if exam_number <= 2:
                return "D"
            if exam_number <= 3:
                return "C"
            if exam_number <= 4:
                return "B"
            if exam_number <= 5:
                return "A"
            return "S"


        def scan_subjects(subjects_root: str | Path = ".subjects") -> List[Dict[str, object]]:
            root = Path(subjects_root)
            if not root.exists():
                return []

            gates: Dict[Path, Dict[str, object]] = {}
            for path in root.rglob("tester.sh"):
                exercise_dir = path.parent
                exam_level = next((part for part in exercise_dir.parts if part.startswith("exam_")), "exam_00")
                gates[exercise_dir] = {
                    "name": exercise_dir.name,
                    "exam": exam_level,
                    "rank": _rank_from_exam(exam_level),
                    "path": str(exercise_dir),
                }
            for path in root.rglob("subject.en.txt"):
                exercise_dir = path.parent.parent if path.parent.name == "attachment" else path.parent
                if exercise_dir not in gates:
                    exam_level = next((part for part in exercise_dir.parts if part.startswith("exam_")), "exam_00")
                    gates[exercise_dir] = {
                        "name": exercise_dir.name,
                        "exam": exam_level,
                        "rank": _rank_from_exam(exam_level),
                        "path": str(exercise_dir),
                    }

            return sorted(gates.values(), key=lambda item: (item["rank"], item["exam"], item["name"]))
        """
    ).lstrip()


def build_dungeon_py() -> str:
    return dedent(
        """
        from __future__ import annotations

        import shutil
        import subprocess
        from pathlib import Path


        SANDBOX_DIR = Path("shadow_dungeon")


        def _reset_sandbox() -> None:
            if SANDBOX_DIR.exists():
                shutil.rmtree(SANDBOX_DIR)
            SANDBOX_DIR.mkdir(parents=True, exist_ok=True)


        def _copy_exercise(exercise_path: Path) -> None:
            for item in exercise_path.iterdir():
                dest = SANDBOX_DIR / item.name
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)


        def enter_gate(gate_path: str | Path) -> tuple[int, str]:
            source = Path(gate_path)
            if not source.exists():
                return 1, "Gate path not found."

            _reset_sandbox()
            _copy_exercise(source)

            tester = SANDBOX_DIR / "tester.sh"
            if not tester.exists():
                return 1, "tester.sh not found in gate."

            tester.chmod(tester.stat().st_mode | 0o111)
            result = subprocess.run(
                ["bash", str(tester)],
                cwd=SANDBOX_DIR,
                text=True,
                capture_output=True,
            )
            output = (result.stdout or "") + (result.stderr or "")
            return result.returncode, output
        """
    ).lstrip()


def build_penalty_py() -> str:
    return dedent(
        """
        from __future__ import annotations

        import subprocess
        from pathlib import Path


        PUNISHMENT_SOURCE = Path(__file__).with_name("punishment.c")


        def run_penalty() -> int:
            binary = Path(__file__).with_name("punishment")
            compile_result = subprocess.run(
                ["cc", str(PUNISHMENT_SOURCE), "-o", str(binary)],
                text=True,
                capture_output=True,
            )
            if compile_result.returncode != 0:
                return compile_result.returncode
            run_result = subprocess.run([str(binary)])
            return run_result.returncode
        """
    ).lstrip()


def build_hud_py() -> str:
    return dedent(
        """
        from __future__ import annotations

        from rich import box
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text


        CONSOLE = Console()


        def render_header() -> None:
            art = Text("SYSTEM ONLINE", style="bold bright_cyan")
            CONSOLE.print(Panel(art, border_style="blue"))


        def render_status(status: dict) -> None:
            table = Table.grid(padding=(0, 1))
            table.add_column(style="bold bright_cyan", justify="right")
            table.add_column(style="white")
            table.add_row("Hunter", str(status.get("name", "")))
            table.add_row("Rank", str(status.get("rank", "")))
            table.add_row("XP", str(status.get("xp", "")))
            table.add_row("Gold", str(status.get("gold", "")))
            table.add_row("Fatigue", str(status.get("fatigue", "")))
            CONSOLE.print(Panel(table, title="Status Window", border_style="blue"))


        def render_gates(gates: list) -> None:
            table = Table(
                title="Available Gates",
                header_style="bold bright_cyan",
                box=box.SIMPLE_HEAVY,
            )
            table.add_column("ID", justify="right", style="bright_cyan", width=4)
            table.add_column("Rank", style="bright_magenta", width=6)
            table.add_column("Exam", style="white")
            table.add_column("Name", style="white")
            for idx, gate in enumerate(gates, start=1):
                table.add_row(str(idx), gate["rank"], gate["exam"], gate["name"])
            if not gates:
                table.add_row("-", "-", "-", "No gates discovered")
            CONSOLE.print(table)
        """
    ).lstrip()


def build_main_py() -> str:
    return dedent(
        """
        from __future__ import annotations

        import json
        from pathlib import Path

        from core.gate_loader import scan_subjects
        from core.hunter import Hunter
        from systems.dungeon import enter_gate
        from systems.penalty import run_penalty
        from ui.hud import CONSOLE, render_gates, render_header, render_status


        SETTINGS_PATH = Path("config/settings.json")


        def load_settings() -> dict:
            if SETTINGS_PATH.exists():
                return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            return {}


        def save_settings(settings: dict) -> None:
            SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
            SETTINGS_PATH.write_text(json.dumps(settings, indent=2), encoding="utf-8")


        def daily_quest_completed() -> bool:
            return True


        def main() -> None:
            settings = load_settings()
            hunter = Hunter(
                name=settings.get("player_name", "Jin-Woo"),
                rank=settings.get("rank", "E"),
                xp=settings.get("xp", 0),
                gold=settings.get("gold", 0),
                fatigue=settings.get("fatigue", 0),
            )

            if not daily_quest_completed():
                run_penalty()

            gates = scan_subjects()
            CONSOLE.clear()
            render_header()
            render_status(hunter.summary())
            render_gates(gates)

            if not gates:
                return
            choice = input("Select Gate ID: ").strip()
            if not choice.isdigit():
                return
            index = int(choice) - 1
            if index < 0 or index >= len(gates):
                return
            gate = gates[index]
            exit_code, output = enter_gate(gate["path"])
            CONSOLE.print(output)
            if exit_code == 0:
                hunter.gain_xp(100)
                hunter.gain_gold(25)
            else:
                hunter.add_fatigue(10)
            save_settings(
                {
                    "player_name": hunter.name,
                    "rank": hunter.rank,
                    "xp": hunter.xp,
                    "gold": hunter.gold,
                    "fatigue": hunter.fatigue,
                    "system_version": settings.get("system_version", "v1.0"),
                }
            )


        if __name__ == "__main__":
            main()
        """
    ).lstrip()


def build_punishment_c() -> str:
    return dedent(
        r"""
        #include <stdio.h>

        int main(void)
        {
            int answer = 0;
            while (1)
            {
                printf("Calculate 34 * 92 + 11? ");
                fflush(stdout);
                if (scanf("%d", &answer) != 1)
                {
                    int ch;
                    while ((ch = getchar()) != '\n' && ch != EOF) {}
                    continue;
                }
                if (answer == 34 * 92 + 11)
                {
                    printf("Correct. Release granted.\n");
                    break;
                }
                printf("Incorrect. Try again.\n");
            }
            return 0;
        }
        """
    ).lstrip()


def install_structure() -> None:
    settings_path = PROJECT_ROOT / "config/settings.json"
    write_file(settings_path, json.dumps(build_settings(), indent=2))

    write_file(PROJECT_ROOT / "core/hunter.py", build_hunter_py())
    write_file(PROJECT_ROOT / "core/gate_loader.py", build_gate_loader_py())
    write_file(PROJECT_ROOT / "systems/dungeon.py", build_dungeon_py())
    write_file(PROJECT_ROOT / "systems/penalty.py", build_penalty_py())
    write_file(PROJECT_ROOT / "systems/punishment.c", build_punishment_c())
    write_file(PROJECT_ROOT / "ui/hud.py", build_hud_py())
    write_file(PROJECT_ROOT / "main.py", build_main_py())


def main() -> None:
    ensure_rich()
    install_structure()
    print("SHADOW_TERMINAL installed.")


if __name__ == "__main__":
    main()
