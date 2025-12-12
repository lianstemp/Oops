import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.status import Status
from rich.layout import Layout
from rich import print as rprint

# Ensure the src directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import get_orchestrator

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
    # Initialize Orchestrator (this might take a second)
    orchestrator = get_orchestrator()
    console.print("[green]✓ System Online[/green]")
    console.print()
    
    # Instructions
    console.print(Panel.fit(
        "Please describe your target and engagement parameters.\n"
        "[bold]Example:[/bold] 'I want to perform a red team assessment on my company website, example.com.'",
        title="Input Required",
        border_style="blue"
    ))
    console.print()
    
    try:
        user_input = Prompt.ask("[bold cyan]>[/bold cyan] Enter command")
        if not user_input:
            console.print("[yellow]No input provided. Exiting.[/yellow]")
            return

        console.print()
        
        # Use a spinner while the agent runs
        with console.status("[bold cyan]Orchestrating agents...[/bold cyan]", spinner="dots"):
            response = orchestrator(user_input)
        
        # Output Display
        console.print()
        console.print(Panel(
            Markdown(str(response)),
            title="[bold green]Report Summary[/bold green]",
            border_style="green"
        ))
        
        console.print()
        console.print("[dim]Detailed artifacts generated in:[/dim] [bold]output/[/bold] (scope.md, intel.md, plan.md)")

    except KeyboardInterrupt:
        console.print("\n[bold red]Operation cancelled by user.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]An error occurred:[/bold red] {e}")

if __name__ == "__main__":
    main()
