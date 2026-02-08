# 42_EXAM Developer Documentation

## Overview
This repository is a fork of the 42_EXAM/GradeMe training environment. The runtime is a compiled C++ binary that presents an `examshell` prompt, manages exam state, and delegates grading to per-exercise shell scripts stored in `.subjects/`. The grading pipeline compiles reference solutions, runs student submissions, and uses `diff` to compare outputs, producing tracebacks when mismatches occur.

## Entry Points
| Entry Point | Type | Purpose |
| --- | --- | --- |
| `.system/launch.sh` | Shell | Bootstraps dependencies, compiles the C++ engine, and executes `.system/a.out`. |
| `.system/main.cpp` | C++ | Implements the interactive shell loop and user commands (including `grademe`). |
| `main.py` | Python | Optional Rich UI wrapper that loads gates and executes shell-based exercises. |
| `system_core.py` | Python | Optional Rich-based wrapper that executes `./grademe.sh` (not present in this repo). |

> **Note:** The canonical entry point for the official 42_EXAM workflow is `.system/launch.sh`, which compiles C++ sources and runs the resulting binary.

## Runtime Flow (High-Level)
1. **Launch/Bootstrap**
   - `.system/launch.sh` checks dependencies (readline, compilers) and compiles the C++ engine into `.system/a.out`.
2. **Interactive Shell**
   - `.system/a.out` provides an `examshell` prompt implemented in `.system/main.cpp`.
3. **Exercise Selection**
   - The C++ engine selects exercises and copies exercise assets into `subjects/` and `.system/grading/`.
4. **Grading**
   - The `grademe` command runs `.system/grading/tester.sh`, which compiles and runs reference and student solutions.
   - Output comparison is handled by the grading scripts (using `diff`), and tracebacks are written into `.system/grading/traceback`.

## Grading Pipeline (Details)
### 1) Exercise Preparation
`exam::prepare_current_ex()` creates working directories (`rendu/`, `subjects/`, `.system/grading/`) and copies exercise files from `.subjects/` into `.system/grading/` and `subjects/`. This is the bridge between static exercise data and the runtime grading environment.

### 2) Grading Entry (Moulinette Trigger)
`exam::grademe()` in `.system/grade_request.cpp` is invoked when a user types `grademe` at the shell prompt. It enforces cooldown rules and calls `exam::grade_request()`.

### 3) Grading Execution
`exam::grade_request()` runs `.system/grading/tester.sh`. The tester script is exercise-specific, copied from `.subjects/.../tester.sh` into `.system/grading/` during preparation.

### 4) Output Comparison & Tracebacks
The standard scripts `.system/auto_correc_program.sh` and `.system/auto_correc_main.sh` demonstrate the canonical grading logic:
- compile reference solution (`source`)
- compile student solution (`final`)
- run both, capture output to files
- use `diff` to compare
If output differs or a timeout occurs, the scripts append structured failure diagnostics to a `traceback` file.

### 5) Pass/Fail
`exam::grade_request()` checks for `.system/grading/passed` to mark success. If missing, it moves the `traceback` into `traces/` and applies penalties.

## Data Layout
### Subjects & Tests
All exercise definitions live under `.subjects/`, organized by track (`PISCINE_PART`, `STUD_PART`), exam, and difficulty level. Each exercise directory typically contains:
- `subject.en.txt` (and sometimes `subject.fr.txt`)
- one or more `.c` / `.cpp` reference implementations
- `tester.sh` (the grader)
- optional attachments (input/output samples)

### Runtime State
- `.system/grading/` is the active grading workspace (copied from `.subjects/`).
- `rendu/` is the student submission directory.
- `subjects/` is a copy of exercise attachments for the student.
- `.system/exam_token/` holds persistent exam metadata.

## Key Components (Map for Hooking a Python System)
| Component | Role | Integration Point |
| --- | --- | --- |
| `.system/launch.sh` | Bootstrapper | Replace/augment with a Python launcher if desired. |
| `.system/main.cpp` | Shell UX & command routing | Mirror `grademe` command in Python. |
| `.system/grade_request.cpp` | Grading orchestration | Python can call `.system/grading/tester.sh` directly. |
| `.system/auto_correc_*.sh` | Grading logic | Reuse logic or wrap in Python to stream output. |
| `.subjects/**/tester.sh` | Exercise-specific grader | Primary hook for executing checks. |

## Suggested Python Hook Strategy
1. Invoke `.system/launch.sh` (or compile the C++ engine directly) to ensure runtime matches the official toolchain.
2. If you want to bypass the C++ shell, mirror the grading pipeline:
   - Select an exercise under `.subjects/`
   - Copy exercise files into `.system/grading/`
   - Execute `.system/grading/tester.sh`
   - Read `.system/grading/traceback` and `.system/grading/passed` for results

## Appendix: Where to Look for Answers
- **Entry point & dependency checks:** `.system/launch.sh`
- **Shell prompt, user commands:** `.system/main.cpp`
- **Grading trigger & pass/fail logic:** `.system/grade_request.cpp`
- **Exercise preparation and asset copying:** `.system/exercise.cpp`
- **Auto-correction diff scripts:** `.system/auto_correc_program.sh`, `.system/auto_correc_main.sh`
- **Exercise bank:** `.subjects/`

## Code Metrics (Snapshot)
- Python: ~395 LOC across 5 files
- Shell: ~15,453 LOC across 128 files
- C/C++: ~11,807 LOC across 289 files
- Largest file by LOC: `.subjects/STUD_PART/exam_03/0/ft_printf/ft_printf.c` (~411 LOC)

## Analysis Commands Used (for this snapshot)
- `find . -maxdepth 3 -print`
- `find .subjects -maxdepth 3 -print`
- `python - <<'PY' ...` (repository scan for LOC and largest file)
- `python - <<'PY' ...` (repository tree snapshot)

## Repository Tree (Snapshot)

```
exam-
├── .gitattributes
├── .github
│   └── FUNDING.yml
├── .subjects
│   ├── PISCINE_PART
│   │   ├── .DS_Store
│   │   ├── exam_01
│   │   │   ├── .DS_Store
│   │   │   ├── 0
│   │   │   │   ├── .DS_Store
│   │   │   │   ├── aff_a
│   │   │   │   │   ├── aff_a.c
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── ft_countdown
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── ft_countdown.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── ft_print_numbers
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── ft_print_numbers.c
│   │   │   │       ├── main.c
│   │   │   │       └── tester.sh
│   │   │   ├── 1
│   │   │   │   ├── .DS_Store
│   │   │   │   ├── hello
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── hello.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── maff_alpha
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── maff_alpha.c
│   │   │   │       └── tester.sh
│   │   │   ├── 2
│   │   │   │   ├── .DS_Store
│   │   │   │   ├── aff_first_param
│   │   │   │   │   ├── aff_first_param.c
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── aff_last_param
│   │   │   │   │   ├── aff_last_param.c
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   └── tester.sh
│   │   │   │   └── aff_z
│   │   │   │       ├── aff_z.c
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       └── tester.sh
│   │   │   ├── 3
│   │   │   │   ├── .DS_Store
│   │   │   │   ├── maff_revalpha
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── maff_revalpha.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── only_a
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── only_a.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── only_z
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── only_z.c
│   │   │   │       └── tester.sh
│   │   │   ├── 4
│   │   │   │   ├── .DS_Store
│   │   │   │   ├── ft_strcpy
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── ft_strcpy.c
│   │   │   │   │   ├── main.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── ft_strlen
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── ft_strlen.c
│   │   │   │       ├── main.c
│   │   │   │       └── tester.sh
│   │   │   ├── 5
│   │   │   │   ├── .DS_Store
│   │   │   │   ├── repeat_alpha
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── repeat_alpha.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── search_and_replace
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── search_and_replace.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── ulstr
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── tester.sh
│   │   │   │       └── ulstr.c
│   │   │   ├── 6
│   │   │   │   ├── .DS_Store
│   │   │   │   ├── first_word
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── first_word.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── ft_putstr
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── ft_putstr.c
│   │   │   │   │   ├── main.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── ft_swap
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── ft_swap.c
│   │   │   │       ├── main.c
│   │   │   │       └── tester.sh
│   │   │   └── 7
│   │   │       ├── .DS_Store
│   │   │       ├── rev_print
│   │   │       │   ├── attachment
│   │   │       │   │   └── subject.en.txt
│   │   │       │   ├── rev_print.c
│   │   │       │   └── tester.sh
│   │   │       ├── rot_13
│   │   │       │   ├── attachment
│   │   │       │   │   └── subject.en.txt
│   │   │       │   ├── rot_13.c
│   │   │       │   └── tester.sh
│   │   │       └── rotone
│   │   │           ├── attachment
│   │   │           │   └── subject.en.txt
│   │   │           ├── rotone.c
│   │   │           └── tester.sh
│   │   ├── exam_02
│   │   │   ├── .DS_Store
│   │   │   ├── 0
│   │   │   │   ├── .DS_Store
│   │   │   │   ├── ft_strcpy
│   │   │   │   │   ├── .DS_Store
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── ft_strcpy.c
│   │   │   │   │   ├── main.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── ft_strlen
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── ft_strlen.c
│   │   │   │   │   ├── main.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── repeat_alpha
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── repeat_alpha.c
│   │   │   │       └── tester.sh
│   │   │   ├── 1
│   │   │   │   ├── .DS_Store
│   │   │   │   ├── search_and_replace
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── search_and_replace.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── ulstr
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── tester.sh
│   │   │   │       └── ulstr.c
│   │   │   ├── 2
│   │   │   │   ├── .DS_Store
│   │   │   │   ├── first_word
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── first_word.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── ft_putstr
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── ft_putstr.c
│   │   │   │   │   ├── main.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── ft_swap
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── ft_swap.c
│   │   │   │       ├── main.c
│   │   │   │       └── tester.sh
│   │   │   ├── 3
│   │   │   │   ├── .DS_Store
│   │   │   │   ├── rev_print
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── rev_print.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── rot_13
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── rot_13.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── rotone
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── rotone.c
│   │   │   │       └── tester.sh
│   │   │   ├── 4
│   │   │   │   ├── .DS_Store
│   │   │   │   ├── ft_atoi
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── ft_atoi.c
│   │   │   │   │   ├── main.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── ft_strdup
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── ft_strdup.c
│   │   │   │   │   ├── main.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── inter
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── inter.c
│   │   │   │       └── tester.sh
│   │   │   ├── 5
│   │   │   │   ├── .DS_Store
│   │   │   │   ├── last_word
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── last_word.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── reverse_bits
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── main.c
│   │   │   │   │   ├── reverse_bits.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── swap_bits
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── main.c
│   │   │   │   │   ├── swap_bits.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── union
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── tester.sh
│   │   │   │       └── union.c
│   │   │   ├── 6
│   │   │   │   ├── .DS_Store
│   │   │   │   ├── alpha_mirror
│   │   │   │   │   ├── alpha_mirror.c
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── do_op
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── do-op.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── ft_strcmp
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── ft_strcmp.c
│   │   │   │   │   ├── main.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── ft_strrev
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── ft_strrev.c
│   │   │   │       ├── main.c
│   │   │   │       └── tester.sh
│   │   │   └── 7
│   │   │       ├── .DS_Store
│   │   │       ├── is_power_of_2
│   │   │       │   ├── attachment
│   │   │       │   │   └── subject.en.txt
│   │   │       │   ├── is_power_of_2.c
│   │   │       │   ├── main.c
│   │   │       │   └── tester.sh
│   │   │       ├── max
│   │   │       │   ├── attachment
│   │   │       │   │   └── subject.en.txt
│   │   │       │   ├── main.c
│   │   │       │   ├── max.c
│   │   │       │   └── tester.sh
│   │   │       ├── print_bits
│   │   │       │   ├── attachment
│   │   │       │   │   └── subject.en.txt
│   │   │       │   ├── main.c
│   │   │       │   ├── print_bits.c
│   │   │       │   └── tester.sh
│   │   │       └── wdmatch
│   │   │           ├── attachment
│   │   │           │   └── subject.en.txt
│   │   │           ├── main.c
│   │   │           ├── tester.sh
│   │   │           └── wdmatch.c
│   │   ├── exam_03
│   │   │   ├── 0
│   │   │   │   ├── ft_atoi
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── ft_atoi.c
│   │   │   │   │   ├── main.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── ft_strdup
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── ft_strdup.c
│   │   │   │   │   ├── main.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── inter
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── inter.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── last_word
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── last_word.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── reverse_bits
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── main.c
│   │   │   │   │   ├── reverse_bits.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── swap_bits
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── main.c
│   │   │   │   │   ├── swap_bits.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── union
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── tester.sh
│   │   │   │       └── union.c
│   │   │   ├── 1
│   │   │   │   ├── alpha_mirror
│   │   │   │   │   ├── alpha_mirror.c
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── do_op
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── do-op.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── ft_strcmp
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── ft_strcmp.c
│   │   │   │   │   ├── main.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── ft_strrev
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── ft_strrev.c
│   │   │   │   │   ├── main.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── is_power_of_2
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── is_power_of_2.c
│   │   │   │   │   ├── main.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── max
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── main.c
│   │   │   │   │   ├── max.c
│   │   │   │   │   └── tester.sh
│   │   │   │   ├── print_bits
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── main.c
│   │   │   │   │   ├── print_bits.c
│   │   │   │   │   └── tester.sh
│   │   │   │   └── wdmatch
│   │   │   │       ├── attachment
│   │   │   │       │   └── subject.en.txt
│   │   │   │       ├── main.c
│   │   │   │       ├── tester.sh
│   │   │   │       └── wdmatch.c
│   │   │   ├── 2
│   │   │   │   ├── add_prime_sum
│   │   │   │   │   ├── 3-1_add_prime_sum.trace
│   │   │   │   │   ├── add_prime_sum.c
│   │   │   │   │   └── attachment
│   │   │   │   │       └── subject.en.txt
│   │   │   │   ├── epur_str
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   ├── examples.txt
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   └── epur_str.c
│   │   │   │   ├── ft_list_size
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── ft_list.h
│   │   │   │   │   ├── ft_list_size.c
│   │   │   │   │   └── README.md
│   │   │   │   ├── ft_rrange
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   └── ft_rrange.c
│   │   │   │   ├── hidenp
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── examples.txt
│   │   │   │   │   └── hidenp.c
│   │   │   │   ├── pgcd
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   ├── examples.txt
│   │   │   │   │   └── pgcd.c
│   │   │   │   ├── print_hex
│   │   │   │   │   ├── attachment
│   │   │   │   │   │   └── subject.en.txt
│   │   │   │   │   └── print_hex.c
│   │   │   │   └── rstr_capitalizer
│   │   │   │       └── attachment
│   │   │   │           ├── examples.txt
│   │   │   │           └── subject.en.txt
│   │   │   └── 3
│   │   │       ├── expand_str
│   │   │       │   ├── attachment
│   │   │       │   │   ├── examples.txt
│   │   │       │   │   └── subject.en.txt
│   │   │       │   └── expand_str.c
│   │   │       ├── ft_atoi_base
│   │   │       │   ├── attachment
│   │   │       │   │   └── subject.en.txt
│   │   │       │   ├── ft_atoi_base.c
│   │   │       │   └── ft_atoi_base_withmain.c
│   │   │       ├── ft_range
│   │   │       │   ├── attachment
│   │   │       │   │   └── subject.en.txt
│   │   │       │   ├── ft_range.c
│   │   │       │   └── ft_range_withmain.c
│   │   │       ├── lcm
│   │   │       │   ├── attachment
│   │   │       │   │   └── subject.en.txt
│   │   │       │   └── lcm.c
│   │   │       ├── paramsum
│   │   │       │   ├── attachment
│   │   │       │   │   ├── examples.txt
│   │   │       │   │   └── subject.en.txt
│   │   │       │   └── paramsum.c
│   │   │       ├── str_capitalizer
│   │   │       │   ├── attachment
│   │   │       │   │   ├── examples.txt
│   │   │       │   │   └── subject.en.txt
│   │   │       │   └── str_capitaliser.c
│   │   │       └── tab_mult
│   │   │           ├── attachment
│   │   │           │   ├── examples.txt
│   │   │           │   └── subject.en.txt
│   │   │           └── tab_mult.c
│   │   └── exam_04
│   │       ├── 0
│   │       │   ├── add_prime_sum
│   │       │   │   ├── 3-1_add_prime_sum.trace
│   │       │   │   ├── add_prime_sum.c
│   │       │   │   └── attachment
│   │       │   │       └── subject.en.txt
│   │       │   ├── epur_str
│   │       │   │   ├── attachment
│   │       │   │   │   ├── examples.txt
│   │       │   │   │   └── subject.en.txt
│   │       │   │   └── epur_str.c
│   │       │   ├── ft_list_size
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   ├── ft_list.h
│   │       │   │   ├── ft_list_size.c
│   │       │   │   └── README.md
│   │       │   ├── ft_rrange
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   └── ft_rrange.c
│   │       │   ├── hidenp
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   ├── examples.txt
│   │       │   │   └── hidenp.c
│   │       │   ├── pgcd
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   ├── examples.txt
│   │       │   │   └── pgcd.c
│   │       │   ├── print_hex
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   └── print_hex.c
│   │       │   └── rstr_capitalizer
│   │       │       ├── attachment
│   │       │       │   └── subject.en.txt
│   │       │       └── examples.txt
│   │       ├── 1
│   │       │   ├── expand_str
│   │       │   │   ├── attachment
│   │       │   │   │   ├── examples.txt
│   │       │   │   │   └── subject.en.txt
│   │       │   │   └── expand_str.c
│   │       │   ├── ft_atoi_base
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   ├── ft_atoi_base.c
│   │       │   │   └── ft_atoi_base_withmain.c
│   │       │   ├── ft_range
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   ├── ft_range.c
│   │       │   │   └── ft_range_withmain.c
│   │       │   ├── lcm
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   └── lcm.c
│   │       │   ├── paramsum
│   │       │   │   ├── attachment
│   │       │   │   │   ├── examples.txt
│   │       │   │   │   └── subject.en.txt
│   │       │   │   └── paramsum.c
│   │       │   ├── str_capitalizer
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   ├── examples.txt
│   │       │   │   └── str_capitaliser.c
│   │       │   └── tab_mult
│   │       │       ├── attachment
│   │       │       │   ├── examples.txt
│   │       │       │   └── subject.en.txt
│   │       │       └── tab_mult.c
│   │       ├── 2
│   │       │   ├── brainfuck
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   └── brainfuck.c
│   │       │   ├── check_mate
│   │       │   │   ├── attachment
│   │       │   │   │   ├── examples.txt
│   │       │   │   │   └── subject.en.txt
│   │       │   │   ├── check_mate.c
│   │       │   │   └── check_mate_withmain.c
│   │       │   ├── flood_fill
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   └── flood_fill.c
│   │       │   ├── fprime
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   ├── fprime.c
│   │       │   │   └── fprime_recursive.c
│   │       │   ├── ft_itoa
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   └── ft_itoa.c
│   │       │   ├── ft_itoa_base
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   └── ft_itoa_base.c
│   │       │   ├── ft_list_foreach
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   ├── ft_list.h
│   │       │   │   └── ft_list_foreach.c
│   │       │   ├── ft_list_remove_if
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   ├── ft_list.h
│   │       │   │   └── ft_list_remove_if.c
│   │       │   ├── ft_split
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   └── ft_split.c
│   │       │   ├── rev_wstr
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   └── rev_wstr.c
│   │       │   ├── rostring
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   └── rostring.c
│   │       │   ├── sort_int_tab
│   │       │   │   ├── attachment
│   │       │   │   │   └── subject.en.txt
│   │       │   │   └── sort_int_tab.c
│   │       │   └── sort_list
│   │       │       ├── attachment
│   │       │       │   └── subject.en.txt
│   │       │       ├── list.h
│   │       │       └── sort_list.c
│   │       └── 3
│   │           ├── biggest_pal
│   │           │   └── attachment
│   │           │       └── subject.en.txt
│   │           ├── brackets
│   │           │   ├── attachment
│   │           │   │   └── subject.en.txt
│   │           │   └── brackets.c
│   │           ├── cycle_detector
│   │           │   ├── attachment
│   │           │   │   └── subject.en.txt
│   │           │   ├── cycle_detector.c
│   │           │   └── list.h
│   │           ├── options
│   │           │   ├── attachment
│   │           │   │   ├── subject.en.txt
│   │           │   │   └── subject.fr.txt
│   │           │   └── options.c
│   │           ├── print_memory
│   │           │   ├── attachment
│   │           │   │   └── subject.en.txt
│   │           │   ├── main.c
│   │           │   └── print_memory.c
│   │           └── rpn_calc
│   │               ├── attachment
│   │               │   └── subject.en.txt
│   │               ├── check.c
│   │               ├── is.c
│   │               ├── main.c
│   │               ├── rpn_calc.c
│   │               └── rpn_calc.h
│   └── STUD_PART
│       ├── exam_02
│       │   ├── 0
│       │   │   ├── first_word
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── first_word.c
│       │   │   │   └── tester.sh
│       │   │   ├── fizzbuzz
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── fizzbuzz.c
│       │   │   │   └── tester.sh
│       │   │   ├── ft_putstr
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── ft_putstr.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── ft_strcpy
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── ft_strcpy.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── ft_strlen
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── ft_strlen.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── ft_swap
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── ft_swap.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── repeat_alpha
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── repeat_alpha.c
│       │   │   │   └── tester.sh
│       │   │   ├── rev_print
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── rev_print.c
│       │   │   │   └── tester.sh
│       │   │   ├── rot_13
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── rot_13.c
│       │   │   │   └── tester.sh
│       │   │   ├── rotone
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── rotone.c
│       │   │   │   └── tester.sh
│       │   │   ├── search_and_replace
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── search_and_replace.c
│       │   │   │   └── tester.sh
│       │   │   └── ulstr
│       │   │       ├── attachment
│       │   │       │   └── subject.en.txt
│       │   │       ├── tester.sh
│       │   │       └── ulstr.c
│       │   ├── 1
│       │   │   ├── alpha_mirror
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── alpha_mirror.c
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   └── tester.sh
│       │   │   ├── camel_to_snake
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── beta
│       │   │   │   ├── camel_to_snake.c
│       │   │   │   └── tester.sh
│       │   │   ├── do_op
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── do_op.c
│       │   │   │   └── tester.sh
│       │   │   ├── ft_atoi
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── ft_atoi.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── ft_strcmp
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── ft_strcmp.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── ft_strcspn
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── ft_strcspn.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── ft_strdup
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── ft_strdup.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── inter
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── inter.c
│       │   │   │   └── tester.sh
│       │   │   ├── is_power_of_2
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── is_power_of_2.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── last_word
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── last_word.c
│       │   │   │   └── tester.sh
│       │   │   ├── max
│       │   │   │   ├── .DS_Store
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── main.c
│       │   │   │   ├── max.c
│       │   │   │   └── tester.sh
│       │   │   ├── print_bits
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── main.c
│       │   │   │   ├── print_bits.c
│       │   │   │   └── tester.sh
│       │   │   ├── snake_to_camel
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── beta
│       │   │   │   ├── snake_to_camel.c
│       │   │   │   └── tester.sh
│       │   │   ├── swap_bits
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── beta
│       │   │   │   ├── main.c
│       │   │   │   ├── swap_bits.c
│       │   │   │   └── tester.sh
│       │   │   └── union
│       │   │       ├── beta
│       │   │       ├── subject.en.txt
│       │   │       ├── tester.sh
│       │   │       └── union.c
│       │   ├── 2
│       │   │   ├── add_prime_sum
│       │   │   │   ├── add_prime_sum.c
│       │   │   │   ├── attachment
│       │   │   │   │   ├── subject.en.txt
│       │   │   │   │   └── subject.fr.txt
│       │   │   │   └── tester.sh
│       │   │   ├── epur_str
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── epur_str.c
│       │   │   │   └── tester.sh
│       │   │   ├── expand_str
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── expand_str.c
│       │   │   │   └── tester.sh
│       │   │   ├── ft_atoi_base
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── ft_atoi_base.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── ft_list_size
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── ft_list_size.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── ft_range
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── ft_range.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── ft_rrange
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── ft_rrange.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── hidenp
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── hidenp.c
│       │   │   │   └── tester.sh
│       │   │   ├── lcm
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── lcm.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── paramsum
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── paramsum.c
│       │   │   │   └── tester.sh
│       │   │   ├── pgcd
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── pgcd.c
│       │   │   │   └── tester.sh
│       │   │   ├── print_hex
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── print_hex.c
│       │   │   │   └── tester.sh
│       │   │   ├── rstr_capitalizer
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── rstr_capitalizer.c
│       │   │   │   └── tester.sh
│       │   │   ├── str_capitalizer
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── str_capitalizer.c
│       │   │   │   └── tester.sh
│       │   │   └── tab_mult
│       │   │       ├── attachment
│       │   │       │   └── subject.en.txt
│       │   │       ├── tab_mult.c
│       │   │       └── tester.sh
│       │   ├── 3
│       │   │   ├── flood_fill
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── beta
│       │   │   │   ├── flood_fill.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── fprime
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── fprime.c
│       │   │   │   └── tester.sh
│       │   │   ├── ft_itoa
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── ft_itoa.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── ft_split
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── beta
│       │   │   │   ├── ft_split.c
│       │   │   │   ├── main.c
│       │   │   │   └── tester.sh
│       │   │   ├── rev_wstr
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── beta
│       │   │   │   ├── rev_wstr.c
│       │   │   │   └── tester.sh
│       │   │   ├── rostring
│       │   │   │   ├── attachment
│       │   │   │   │   └── subject.en.txt
│       │   │   │   ├── beta
│       │   │   │   ├── rostring.c
│       │   │   │   └── tester.sh
│       │   │   └── sort_list
│       │   │       ├── attachment
│       │   │       │   ├── list.h
│       │   │       │   └── subject.en.txt
│       │   │       ├── beta
│       │   │       ├── list.h
│       │   │       ├── main.c
│       │   │       ├── sort_list.c
│       │   │       └── tester.sh
│       │   └── need_correction
│       │       ├── flood_fill
│       │       │   ├── attachment
│       │       │   │   └── subject.en.txt
│       │       │   └── flood_fill.c
│       │       ├── ft_list_foreach
│       │       │   ├── attachment
│       │       │   │   └── subject.en.txt
│       │       │   └── ft_list_foreach.c
│       │       ├── ft_list_remove_if
│       │       │   ├── attachment
│       │       │   │   └── subject.en.txt
│       │       │   └── ft_list_remove_if.c
│       │       ├── ft_split
│       │       │   ├── attachment
│       │       │   │   ├── subject.en.txt
│       │       │   │   └── subject.fr.txt
│       │       │   └── ft_split.c
│       │       ├── rev_wstr
│       │       │   ├── attachment
│       │       │   │   └── subject.en.txt
│       │       │   └── rev_wstr.c
│       │       ├── rostring
│       │       │   ├── attachment
│       │       │   │   └── subject.en.txt
│       │       │   └── rostring.c
│       │       ├── sort_int_tab
│       │       │   ├── attachment
│       │       │   │   └── subject.en.txt
│       │       │   └── sort_int_tab.c
│       │       └── sort_list
│       │           ├── attachment
│       │           │   └── sort_list.subject.en.txt
│       │           ├── ft_sort_list.c
│       │           ├── sort_list.c
│       │           ├── sort_list.list.h
│       │           └── sort_list.trace
│       ├── exam_03
│       │   ├── .DS_Store
│       │   └── 0
│       │       ├── ft_printf
│       │       │   ├── .DS_Store
│       │       │   ├── attachment
│       │       │   │   └── subject.en.txt
│       │       │   ├── ft_printf.c
│       │       │   ├── main.c
│       │       │   └── tester.sh
│       │       └── get_next_line
│       │           ├── .DS_Store
│       │           ├── attachment
│       │           │   └── subject.en.txt
│       │           ├── get_next_line.c
│       │           ├── mainboc.c
│       │           ├── mainstud.c
│       │           ├── test
│       │           └── tester.sh
│       ├── exam_04
│       │   ├── .DS_Store
│       │   └── 0
│       │       ├── .DS_Store
│       │       └── microshell
│       │           ├── .DS_Store
│       │           ├── attachment
│       │           │   ├── subject.en.txt
│       │           │   └── subject.fr.txt
│       │           ├── microshell.c
│       │           ├── test.sh
│       │           └── tester.sh
│       ├── exam_05
│       │   ├── .DS_Store
│       │   ├── 0
│       │   │   ├── .DS_Store
│       │   │   └── cpp_module00
│       │   │       ├── attachment
│       │   │       │   └── subject.en.txt
│       │   │       ├── main.cpp
│       │   │       ├── tester.sh
│       │   │       ├── Warlock.cpp
│       │   │       └── Warlock.hpp
│       │   ├── 1
│       │   │   ├── .DS_Store
│       │   │   └── cpp_module01
│       │   │       ├── ASpell.cpp
│       │   │       ├── ASpell.hpp
│       │   │       ├── ATarget.cpp
│       │   │       ├── ATarget.hpp
│       │   │       ├── attachment
│       │   │       │   └── subject.en.txt
│       │   │       ├── Dummy.cpp
│       │   │       ├── Dummy.hpp
│       │   │       ├── Fwoosh.cpp
│       │   │       ├── Fwoosh.hpp
│       │   │       ├── main.cpp
│       │   │       ├── tester.sh
│       │   │       ├── Warlock.cpp
│       │   │       └── Warlock.hpp
│       │   └── 2
│       │       └── cpp_module02
│       │           ├── ASpell.cpp
│       │           ├── ASpell.hpp
│       │           ├── ATarget.cpp
│       │           ├── ATarget.hpp
│       │           ├── attachment
│       │           │   └── subject.en.txt
│       │           ├── BrickWall.cpp
│       │           ├── BrickWall.hpp
│       │           ├── Dummy.cpp
│       │           ├── Dummy.hpp
│       │           ├── Fireball.cpp
│       │           ├── Fireball.hpp
│       │           ├── Fwoosh.cpp
│       │           ├── Fwoosh.hpp
│       │           ├── main.cpp
│       │           ├── Polymorph.cpp
│       │           ├── Polymorph.hpp
│       │           ├── SpellBook.cpp
│       │           ├── SpellBook.hpp
│       │           ├── TargetGenerator.cpp
│       │           ├── TargetGenerator.hpp
│       │           ├── tester.sh
│       │           ├── Warlock.cpp
│       │           └── Warlock.hpp
│       └── exam_06
│           └── 0
│               └── mini_serv
│                   ├── attachment
│                   │   ├── main.c
│                   │   └── subject.en.txt
│                   ├── catchmsg.sh
│                   ├── eof_test
│                   ├── findport.sh
│                   ├── normal.output
│                   ├── other_long_msg.txt
│                   ├── test_eof.sh
│                   ├── test_miniserv.sh
│                   ├── tester.sh
│                   └── very_long_msg.txt
├── .system
│   ├── auto_correc_main.sh
│   ├── auto_correc_program.sh
│   ├── CGV.txt
│   ├── checkreadline.cpp
│   ├── data_persistence.cpp
│   ├── data_sender.sh
│   ├── exam.cpp
│   ├── exam.hpp
│   ├── exam_token
│   │   └── .demo_token
│   ├── exercise.cpp
│   ├── exercise.hpp
│   ├── grade_request.cpp
│   ├── launch.sh
│   ├── main.cpp
│   ├── menu.cpp
│   ├── qrcode
│   ├── qrcodesponsor
│   └── utils.cpp
├── config
│   └── gates.json
├── CONTRIBUTING.md
├── DEVELOPER_DOCS.md
├── LICENSE
├── main.py
├── Makefile
├── modules
│   ├── gate_loader.py
│   └── interface.py
├── README.md
├── system_core.py
└── system_utils.py
```
