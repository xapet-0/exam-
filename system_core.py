import subprocess
from typing import Iterable

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.traceback import install

CONSOLE = Console()
THEME_ACCENT = "bright_cyan"
THEME_SUCCESS = "bright_green"
THEME_FAILURE = "bright_red"


def stream_process_output(process: subprocess.Popen) -> Iterable[str]:
    if process.stdout is None:
        return []
    for line in process.stdout:
        yield line.rstrip("\n")


def run_grading_logic() -> int:
    command = "./grademe.sh"
    CONSOLE.print(Panel(f"Executing: [bold]{command}[/]", border_style=THEME_ACCENT))
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    for line in stream_process_output(process):
        if line.strip():
            CONSOLE.print(line)

    return process.wait()


def render_header() -> None:
    title = Text("42_EXAM // GRADEME LAUNCHER", style="bold bright_cyan")
    subtitle = Text("Automated grading wrapper", style="bright_white")
    CONSOLE.print(Panel(Text.assemble(title, "\n", subtitle), border_style=THEME_ACCENT))


def render_footer(exit_code: int) -> None:
    status_text = "GRADEME COMPLETED"
    style = THEME_SUCCESS if exit_code == 0 else THEME_FAILURE
    CONSOLE.print(Panel(Text(status_text, style=style), border_style=style))
    if exit_code != 0:
        CONSOLE.print(
            Text(
                "Non-zero exit detected. Review the output above for details.",
                style="bright_yellow",
            )
        )


def main() -> None:
    install(show_locals=False)
    CONSOLE.clear()
    render_header()
    exit_code = run_grading_logic()
    render_footer(exit_code)


if __name__ == "__main__":
    main()
