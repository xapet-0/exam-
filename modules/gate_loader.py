import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Gate:
    gate_id: str
    name: str
    rank: str
    command: str
    xp_reward: int


def load_gates(config_path: str = "config/gates.json") -> List[Gate]:
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Gate config not found: {config_file}")

    payload = json.loads(config_file.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Gate config must be a list of gate entries.")

    gates: List[Gate] = []
    for entry in payload:
        if not isinstance(entry, dict):
            raise ValueError("Each gate entry must be an object.")
        gates.append(
            Gate(
                gate_id=str(entry.get("id", "unknown")),
                name=str(entry.get("name", "Unnamed Gate")),
                rank=str(entry.get("rank", "?")),
                command=str(entry.get("command", "")),
                xp_reward=int(entry.get("xp_reward", 0)),
            )
        )
    return gates
