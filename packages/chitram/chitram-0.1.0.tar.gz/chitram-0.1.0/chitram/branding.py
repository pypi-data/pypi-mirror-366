from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

def show_creator_links():
    text = Text()

    text.append("🚀 Created by ", style="bold white")
    text.append("Aman Mishra\n", style="bold red")
    text.append("\n")

    text.append("📺 YouTube: ", style="bold yellow")
    text.append("https://www.youtube.com/channel/UCuYpMYOiuQyGgdM9LXupLEg\n", style="italic blue link https://www.youtube.com/channel/UCuYpMYOiuQyGgdM9LXupLEg")

    text.append("📢 Telegram Channel: ", style="bold green")
    text.append("https://t.me/jarvisbyamanchannel\n", style="italic blue link https://t.me/jarvisbyamanchannel")

    text.append("💬 Telegram Discussion: ", style="bold magenta")
    text.append("https://t.me/jarvisbyaman", style="italic blue link https://t.me/jarvisbyaman")

    panel = Panel(
        text,
        title="[b bright_cyan]🌟 Connect with Aman Automates[/b bright_cyan]",
        subtitle="🛠️ Let's Build the Future with AI",
        title_align="center",
        subtitle_align="center",
        style="white on black",
        border_style="dim cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    )

    console.print(panel)