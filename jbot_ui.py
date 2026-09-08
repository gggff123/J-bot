import sys
import time
import random
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich import box
except ImportError:
    print("Missing dependency 'rich'. Install with: pip install rich")
    sys.exit(1)

console = Console()

# ---------------------------------------------------------------------
# User message rendering (green panel, right-aligned) — matches Nova X
# ---------------------------------------------------------------------
def render_user_message(user_input: str):
    console.print(Panel(
        user_input,
        title="[bold green]you[/bold green]",
        title_align="right",
        border_style="green",
        box=box.ROUNDED,
    ))

# ---------------------------------------------------------------------
# Assistant reply rendering (magenta panel, typewriter effect) — matches Nova X exactly
# ---------------------------------------------------------------------
def render_reply(reply: str):
    """
    Renders an AI reply, splitting out code blocks into plain, unboxed text
    so they can be copied cleanly without box-drawing characters.
    """
    import re

    segments = []
    pos = 0
    fence_re = re.compile(r"```([a-zA-Z0-9_+\-]*)\n(.*?)```", re.DOTALL)
    for m in fence_re.finditer(reply):
        if m.start() > pos:
            prose = reply[pos:m.start()]
            if prose.strip():
                segments.append(("prose", None, prose))
        lang = m.group(1).strip()
        code = m.group(2)
        segments.append(("code", lang, code))
        pos = m.end()
    if pos < len(reply):
        tail = reply[pos:]
        if tail.strip():
            segments.append(("prose", None, tail))

    if not segments:
        segments = [("prose", None, reply)]

    for kind, lang, content in segments:
        if kind == "prose":
            _render_prose_panel(content.strip("\n"))
        else:
            label = lang if lang else "code"
            console.print(f"[dim]— {label} —[/dim]")
            console.print(content.strip("\n"), highlight=False, markup=False)
            console.print(f"[dim]— end {label} —[/dim]")

def _render_prose_panel(text: str):
    if not text:
        return

    out = ""
    panel = Panel(
        out,
        title="[bold magenta]J-BOT[/bold magenta]",
        title_align="left",
        border_style="magenta",
        box=box.ROUNDED,
    )

    with Live(panel, console=console, refresh_per_second=30, transient=False) as live:
        for char in text:
            out += char
            panel = Panel(
                out,
                title="[bold magenta]J-BOT[/bold magenta]",
                title_align="left",
                border_style="magenta",
                box=box.ROUNDED,
            )
            live.update(panel)

            if random.random() < 0.7:
                time.sleep(0.008)
            else:
                time.sleep(0.04)

# ---------------------------------------------------------------------
# Help table — clean, aligned, matches Nova X's style
# ---------------------------------------------------------------------
def print_help():
    table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE)
    table.add_column("Command", style="magenta")
    table.add_column("Description", style="white")
    table.add_row("/build <desc>", "Build a project (code generation)")
    table.add_row("/website <desc>", "Build a website quickly")
    table.add_row("/search <query>", "Search the internet")
    table.add_row("/task <name> <cmd> <cron>", "Schedule a task")
    table.add_row("/tasks", "List scheduled tasks")
    table.add_row("/sandbox", "List sandbox files")
    table.add_row("/python", "Run Python code")
    table.add_row("/bash <cmd>", "Run Bash code in sandbox")
    table.add_row("/alias <name> <cmd>", "Create alias")
    table.add_row("/aliases", "List all aliases")
    table.add_row("/image <prompt>", "Generate image with Pollinations API")
    table.add_row("/images", "List all generated images")
    table.add_row("/image-delete <filename>", "Delete an image")
    table.add_row("/image-copy <file> <dest>", "Copy image to sandbox/project")
    table.add_row("/mem-add KEY VALUE", "Add permanent memory entry (survives restart)")
    table.add_row("/mem-get", "View all permanent memory")
    table.add_row("/mem-delete KEY", "Delete permanent memory entry")
    table.add_row("/mem-clear", "Delete all permanent memory")
    table.add_row("/mem-chat", "View current chat message count")
    table.add_row("/help", "Show this help")
    console.print(table)
    console.print("\n[dim]💡 Press [bold]Ctrl+X[/bold] to cancel current request[/dim]")
    console.print("[dim]💡 J-BOT also has skills, memory, image gen, process tracking, and more that it uses on its own during a task — this list is just the commands YOU type directly.[/dim]\n")

# ---------------------------------------------------------------------
# Notification — matches Nova X's stub
# ---------------------------------------------------------------------
def send_notification(title: str, message: str, priority: str = "default"):
    """Send a system notification (stub for now)."""
    console.print(f"[dim]📢 NOTIFICATION: {title} – {message}[/dim]")