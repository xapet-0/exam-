from datetime import date
import json
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt

from modules.gate_loader import load_gates
from modules.interface import build_hud
from system_utils import (
    calculate_level,
    load_daily_state,
    play_level_up_animation,
    run_command,
    run_penalty_quest,
    save_daily_state,
)

CONSOLE = Console()
PLAYER_STATE_PATH = Path("data/player_state.json")

DEFAULT_DAILY_QUESTS = [
    {"name": "Physical: 20m workout", "completed": False},
    {"name": "Mental: 10m meditation", "completed": False},
    {"name": "Coding: 45m focused session", "completed": False},
]


def load_player_state() -> dict:
    if PLAYER_STATE_PATH.exists():
        return json.loads(PLAYER_STATE_PATH.read_text(encoding="utf-8"))
    return {"xp": 0, "fatigue": 0, "gold": 0}


def save_player_state(state: dict) -> None:
    PLAYER_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLAYER_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def refresh_daily_quests() -> list:
    state = load_daily_state()
    today = date.today().isoformat()
    if state["date"] != today:
        incomplete = [q for q in state.get("quests", []) if not q.get("completed")]
        if state["date"] is not None and incomplete:
            run_penalty_quest()
        state = {"date": today, "quests": [dict(q) for q in DEFAULT_DAILY_QUESTS]}
        save_daily_state(state)
    return state["quests"]


def toggle_daily_quest(quests: list) -> None:
    CONSOLE.print("\nDaily Quests:")
    for index, quest in enumerate(quests, start=1):
        status = "[x]" if quest["completed"] else "[ ]"
        CONSOLE.print(f" {index}. {status} {quest['name']}")

    choice = Prompt.ask("Toggle which quest? (number)", default="0")
    if not choice.isdigit():
        return
    selection = int(choice)
    if 1 <= selection <= len(quests):
        quests[selection - 1]["completed"] = not quests[selection - 1]["completed"]
        save_daily_state({"date": date.today().isoformat(), "quests": quests})


def main() -> None:
    gates = load_gates()
    player_state = load_player_state()
    daily_quests = refresh_daily_quests()

    while True:
        level_info = calculate_level(player_state["xp"])
        stats = {
            "level": level_info["level"],
            "next_level_xp": level_info["next_level_xp"],
            "xp": player_state["xp"],
            "fatigue": player_state["fatigue"],
            "gold": player_state["gold"],
        }

        CONSOLE.clear()
        CONSOLE.print(build_hud(gates, stats, daily_quests))
        choice = Prompt.ask("Action").strip().lower()

        if choice in {"q", "quit", "exit"}:
            save_player_state(player_state)
            break
        if choice in {"d", "daily"}:
            toggle_daily_quest(daily_quests)
            continue
        if not choice.isdigit():
            continue

        gate_index = int(choice) - 1
        if gate_index < 0 or gate_index >= len(gates):
            continue

        gate = gates[gate_index]
        before_level = level_info["level"]
        exit_code = run_command(gate.command)
        if exit_code == 0:
            player_state["xp"] += gate.xp_reward
            player_state["gold"] += gate.xp_reward // 10
            player_state["fatigue"] += 5

            new_level = calculate_level(player_state["xp"])["level"]
            if new_level > before_level:
                play_level_up_animation(new_level)
        save_player_state(player_state)


if __name__ == "__main__":
    main()
