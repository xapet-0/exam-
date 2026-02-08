from __future__ import annotations

from pathlib import Path
from typing import Dict, List


def _extract_exam_level(path: Path) -> str:
    for part in path.parts:
        if part.startswith("exam_"):
            return part
    return "unknown"


def _resolve_exercise_dir(subject_file: Path) -> Path:
    if subject_file.name == "tester.sh":
        return subject_file.parent
    if subject_file.parent.name == "attachment":
        return subject_file.parent.parent
    return subject_file.parent


def scan_subjects(subjects_root: str | Path = ".subjects") -> List[Dict[str, object]]:
    root = Path(subjects_root)
    if not root.exists():
        return []

    exercise_dirs: Dict[Path, Dict[str, object]] = {}

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name not in {"subject.en.txt", "tester.sh"}:
            continue
        exercise_dir = _resolve_exercise_dir(path)
        if exercise_dir not in exercise_dirs:
            exercise_dirs[exercise_dir] = {
                "name": exercise_dir.name,
                "level": _extract_exam_level(exercise_dir),
                "path": str(exercise_dir),
                "has_subject": False,
                "has_tester": False,
            }
        entry = exercise_dirs[exercise_dir]
        if path.name == "subject.en.txt":
            entry["has_subject"] = True
        if path.name == "tester.sh":
            entry["has_tester"] = True

    return sorted(
        exercise_dirs.values(),
        key=lambda item: (str(item["level"]), str(item["name"])),
    )
