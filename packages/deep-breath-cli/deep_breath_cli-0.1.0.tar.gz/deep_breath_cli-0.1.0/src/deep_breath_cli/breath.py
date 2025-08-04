import os
import time
import typer
from rich.console import Console
from rich.progress import track
from typing_extensions import Annotated


PATTERNS: dict[str, list[tuple[int, str]]] = {
    "4-7-8": [
        (4, "[blue]Breathe in..."),
        (7, "[green]Hold..."),
        (8, "[dark_orange]Breathe out..."),
    ],
    "4-4-4-4": [
        (4, "[blue]Breathe in..."),
        (4, "[green]Hold..."),
        (4, "[dark_orange]Breathe out..."),
        (4, "[green]Hold..."),
    ],
}


app = typer.Typer()


def breath_phase(duration: int, message: str):
    """Breathing phase with a message."""
    for value in track(range(duration), description=message):
        time.sleep(1)


@app.command()
def presets():
    """Display available breathing patterns."""
    console = Console()
    console.print("Available breathing patterns:", style="bold")
    for pattern, phases in PATTERNS.items():
        phases_display: list = []
        for duration, message in phases:
            phases_display.append(f"{duration}s {message}")
        phases_str = "[white], ".join(phases_display)
        console.print(f"  {pattern}: {phases_str}")
    console.print(
        "\nYou can use these patterns with the --pattern option.", style="dim"
    )


@app.command("start")
def breath(
    cycle: Annotated[
        int, typer.Option(help="The number of cycle you want to breathe.")
    ] = 4,
    pattern: Annotated[
        str, typer.Option(help="The pattern you want to breath with.")
    ] = "4-7-8",
):
    """Main function to start the breathing cycle."""
    print("Hello from deep-breathe-cli!")
    typer.confirm("Do you want to start a breathing cycle?", abort=True)
    if cycle < 1:
        print("Cycle must be at least 1. Setting to 1.")
        cycle = 1
    print(f"Starting a breathing cycle of {cycle} cycles...")
    time.sleep(2)

    if pattern not in PATTERNS:
        print(f"Pattern '{pattern}' not found. Using default pattern '4-7-8'.")
        pattern = "4-7-8"

    for cycle_number in range(cycle):
        os.system("clear")  # Clear the console for better visibility
        print(f"Cycle {cycle_number + 1} of {cycle}:")
        for duration, message in PATTERNS[pattern]:
            breath_phase(duration, message)
        os.system("clear")
    print("Cycle complete! Take a moment to relax.")


if __name__ == "__main__":
    # typer.run(main)
    app()
