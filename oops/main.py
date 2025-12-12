import os
import sys
import logging
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.layout import Layout
from rich import print as rprint
from rich.style import Style

from oops.agents.orchestrator import get_orchestrator

# Configure logging to suppress noise from libraries
logging.basicConfig(level=logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("strands").setLevel(logging.ERROR)

def main():
    load_dotenv()
    console = Console()
    
    # Elegant Header
    header = Panel(
        "[bold cyan]Oops[/bold cyan] - [italic]Open Source Offensive Security Agent[/italic]\n"
        "[dim]Red Team Orchestrator | Powered by Strands Agents[/dim]",
        border_style="cyan",
        expand=False
    )
    console.print(header)
    console.print()

    print("Initializing Oops Orchestrator...", end="\r")
    # Initialize Orchestrator
    try:
        orchestrator = get_orchestrator()
    except Exception as e:
        console.print(f"[bold red]Failed to initialize orchestrator:[/bold red] {e}")
        return

    console.print("[green]✓ System Online[/green]    ")
    console.print()
    
    # Instructions
    console.print(
        "[dim]Enter your instructions below. Type [bold]exit[/bold] or [bold]quit[/bold] to stop.[/dim]\n"
        "[bold]Example:[/bold] 'I want to perform a red team assessment on my company website, example.com.'"
    )
    console.print()
    
    while True:
        try:
            # Custom input prompt style
            user_input = Prompt.ask("[bold cyan]Oops[/bold cyan] [bold]>[/bold]")
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Shutting down systems. Goodbye.[/yellow]")
                break
                
            if user_input.lower() in ["clear", "cls"]:
                console.clear()
                console.print(header)
                continue
            
            console.print()
            
            # Use a spinner while the agent runs
            with console.status("[bold cyan]Orchestrating agents...[/bold cyan]", spinner="dots"):
                # Call the orchestrator
                response = orchestrator(user_input)
            
            # Output Display - Clean Markdown rendering
            console.print(Markdown(str(response)))
            console.print()
            
            console.print("[dim]Artifacts updated in:[/dim] [bold]output/[/bold]")
            console.print(Panel("", border_style="dim", expand=True, title="[dim]ready[/dim]", title_align="right"))
            console.print()

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Interrupted. Type 'exit' to quit.[/bold yellow]")
            continue
        except Exception as e:
            console.print(f"\n[bold red]An error occurred:[/bold red] {e}")
            continue

if __name__ == "__main__":
    main()