from datetime import date
from typing import List, Dict

from rich import box
from rich.align import Align
from rich.console import Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from modules.gate_loader import Gate


THEME_BORDER = "cyan"
THEME_TITLE = "bold cyan"
THEME_ACCENT = "bright_cyan"
THEME_WARNING = "bright_magenta"


def build_stats_panel(stats: Dict[str, int]) -> Panel:
    table = Table.grid(padding=(0, 1))
    table.add_column(justify="right", style="bright_cyan", width=10)
    table.add_column(justify="left", style="white")
    table.add_row("Level", str(stats["level"]))
    table.add_row("XP", f"{stats['xp']} / {stats['next_level_xp']}")
    table.add_row("Fatigue", str(stats["fatigue"]))
    table.add_row("Gold", str(stats["gold"]))
    return Panel(
        table,
        title="SYSTEM STATUS",
        border_style=THEME_BORDER,
        padding=(1, 2),
    )


def build_gate_table(gates: List[Gate]) -> Table:
    table = Table(
        title="DUNGEON SELECT",
        title_style=THEME_TITLE,
        header_style=THEME_ACCENT,
        box=box.SIMPLE_HEAVY,
        expand=True,
    )
    table.add_column("#", style=THEME_ACCENT, justify="right", width=3)
    table.add_column("Gate", style="white")
    table.add_column("Rank", style="bright_blue", justify="center", width=6)
    table.add_column("XP", style="bright_green", justify="right", width=6)

    for index, gate in enumerate(gates, start=1):
        table.add_row(str(index), gate.name, gate.rank, str(gate.xp_reward))

    if not gates:
        table.add_row("-", "No gates loaded", "-", "-")

    return table


def build_daily_quest_panel(daily_quests: List[Dict[str, object]]) -> Panel:
    table = Table.grid(padding=(0, 1))
    table.add_column(style="bright_green")
    table.add_column(style="white")
    for quest in daily_quests:
        status = "[x]" if quest["completed"] else "[ ]"
        table.add_row(status, quest["name"])

    subtitle = f"Daily Cycle: {date.today().isoformat()}"
    return Panel(
        table,
        title="DAILY QUESTS",
        subtitle=subtitle,
        border_style=THEME_BORDER,
        padding=(1, 2),
    )


def build_hud(gates: List[Gate], stats: Dict[str, int], daily_quests: List[Dict[str, object]]) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3),
    )

    title = Text("SHADOW_CODER // SYSTEM", style=THEME_TITLE)
    layout["header"].update(Align.center(title))

    body = Layout()
    body.split_row(
        Layout(name="stats", size=32),
        Layout(name="gates", ratio=2),
    )
    body["stats"].update(build_stats_panel(stats))
    body["gates"].update(Panel(build_gate_table(gates), border_style=THEME_BORDER))

    layout["body"].update(body)

    footer_group = Group(
        build_daily_quest_panel(daily_quests),
        Align.center(
            Text("Select gate number, [D]aily quest toggle, or [Q]uit", style=THEME_WARNING)
        ),
    )
    layout["footer"].update(footer_group)

    return layout
