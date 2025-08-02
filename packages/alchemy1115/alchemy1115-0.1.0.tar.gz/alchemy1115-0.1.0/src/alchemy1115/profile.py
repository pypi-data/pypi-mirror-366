import typer
from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.text import Text
from rich.live import Live
from rich.style import Style
from time import sleep

app = typer.Typer()


def create_content():
    content = Text()
    content.append("Ryotaro Harada（あるけみー）\n\n", style="bold cyan")
    content.append("  Awards:        ", style="yellow")
    content.append("2024/2025 Japan AWS All Certifications Engineers\n")
    content.append("  Certifcations: ", style="yellow")
    content.append("AWSx14, IPA AP/NW/SC, Registered Scrum Master\n\n")

    content.append("  [SNS]\n", style="bold cyan")
    content.append("  X:             ", style="italic bright_green")
    content.append("https://x.com/symphonius_ryo\n")
    content.append("  Qiita:         ", style="italic bright_green")
    content.append("https://qiita.com/ry-harada\n")
    content.append("  Speaker Deck:  ", style="italic bright_green")
    content.append("https://speakerdeck.com/alchemy1115\n")
    content.append("  GitHub:        ", style="italic bright_green")
    content.append("https://github.com/alchemy-1115\n")
    
    return content


@app.command()
def main():
    full_content = create_content()
    lines = full_content.split("\n")
    console = Console()
    with Live(console=console, refresh_per_second=20) as live:
        content = Text()
        for line in lines:
            for char in line:
                content.append(char)
                panel = Panel(
                    Align.center(content, vertical="middle"),
                    border_style="white",
                    expand=False,
                )
                live.update(panel)
                sleep(0.02)
            content.append("\n")
            live.update(panel)
            sleep(0.1)
        for i in range(1, 50):
            panel.border_style = Style(color=f"color({i*5})")
            live.update(panel)
            sleep(0.1)


if __name__ == "__main__":
    app()