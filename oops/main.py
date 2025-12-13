import os
import sys
import logging
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich import print as rprint

from oops.agents.orchestrator import get_orchestrator
from oops.session import SessionManager, SessionStorage
from oops.workflow import ApprovalWorkflow, WorkflowPhases
from oops.tools import session_tools

# Configure logging to suppress noise from libraries
logging.basicConfig(level=logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("strands").setLevel(logging.ERROR)


def show_header(console: Console):
    """Display application header."""
    header = Panel(
        "[bold cyan]Oops[/bold cyan] - [italic]Interactive Red Team Orchestrator[/italic]\n"
        "[dim]Session-Based Security Assessment | Powered by AI[/dim]",
        border_style="cyan",
        expand=False
    )
    console.print(header)
    console.print()


def check_sandbox_status(console: Console):
    """Check and display sandbox status."""
    from oops.sandbox import SandboxClient
    sandbox = SandboxClient()
    status = sandbox.get_status()
    
    if status["docker_available"]:
        if status["container_running"]:
            console.print("[green]✓ Sandbox Active[/green] - Tools will run in isolated container")
        elif status["image_available"]:
            console.print("[yellow]⚠ Sandbox Inactive[/yellow] - Starting sandbox...")
            if sandbox.start():
                console.print("[green]✓ Sandbox Started[/green]")
            else:
                console.print("[yellow]⚠ Sandbox Failed to Start[/yellow] - Tools will run locally")
        else:
            console.print("[yellow]⚠ Sandbox Image Not Found[/yellow] - Run: docker-compose build")
            console.print("[dim]Tools will run locally (not recommended)[/dim]")
    else:
        console.print("[yellow]⚠ Docker Not Available[/yellow] - Tools will run locally")
        console.print("[dim]For isolated execution, install Docker and run: docker-compose up -d[/dim]")


def handle_command(command: str, session_manager: SessionManager, console: Console) -> bool:
    """Handle special commands.
    
    Args:
        command: User command
        session_manager: Session manager instance
        console: Rich console
    
    Returns:
        True if command was handled, False otherwise
    """
    cmd = command.lower().strip()
    
    if cmd in ["exit", "quit", "q"]:
        console.print("[yellow]Shutting down systems. Goodbye.[/yellow]")
        return True
    
    if cmd in ["clear", "cls"]:
        console.clear()
        show_header(console)
        return True
    
    if cmd in ["/sessions", "/list"]:
        # List all sessions
        sessions = session_manager.list_sessions()
        if not sessions:
            console.print("[yellow]No sessions found.[/yellow]")
        else:
            console.print("[bold]Active Sessions:[/bold]")
            for session in sessions:
                sid = session["session_id"][:8]
                target = session.get("target", "unknown")
                phase = session.get("phase", "unknown")
                status = session.get("status", "unknown")
                console.print(f"  [{sid}] {target} - Phase: {phase} - Status: {status}")
        return True
    
    if cmd.startswith("/switch "):
        # Switch session
        session_id = cmd.split(" ", 1)[1].strip()
        try:
            session_manager.set_current_session(session_id)
            console.print(f"[green]✓ Switched to session: {session_id[:8]}[/green]")
        except Exception as e:
            console.print(f"[red]✗ Failed to switch session: {e}[/red]")
        return True
    
    if cmd in ["/help", "help", "?"]:
        console.print(Panel(
            "[bold]Available Commands:[/bold]\n\n"
            "  /sessions, /list    - List all sessions\n"
            "  /switch <id>        - Switch to a session\n"
            "  /help, help, ?      - Show this help\n"
            "  clear, cls          - Clear screen\n"
            "  exit, quit, q       - Exit Oops\n\n"
            "[bold]Workflow:[/bold]\n"
            "  1. Provide target URL\n"
            "  2. Review and approve scope.md\n"
            "  3. Review and approve intel.md\n"
            "  4. Review and approve plan.md\n"
            "  5. Watch execution with progress tracking",
            title="[cyan]Help[/cyan]",
            border_style="cyan"
        ))
        return True
    
    return False


def main():
    load_dotenv()
    console = Console()
    
    # Show header
    show_header(console)
    
    # Initialize components
    print("Initializing Oops Orchestrator...", end="\r")
    try:
        orchestrator = get_orchestrator()
    except Exception as e:
        console.print(f"[bold red]Failed to initialize orchestrator:[/bold red] {e}")
        return
    
    console.print("[green]✓ System Online[/green]    ")
    
    # Check sandbox
    check_sandbox_status(console)
    console.print()
    
    # Initialize session manager
    session_manager = SessionManager()
    approval_workflow = ApprovalWorkflow()
    workflow_phases = WorkflowPhases(session_manager, approval_workflow)
    
    # Initialize session tools with session manager
    session_tools.set_session_manager(session_manager)
    
    # Instructions
    console.print(
        "[dim]Enter target URL to start a new assessment session.[/dim]\n"
        "[dim]Type [bold]/help[/bold] for commands, [bold]exit[/bold] to quit.[/dim]"
    )
    console.print()
    
    # Main loop
    while True:
        try:
            # Get current session info
            current_session = session_manager.get_current_session()
            if current_session:
                session_id_short = current_session[:8]
                prompt_text = f"[bold cyan]Oops[/bold cyan] [dim]({session_id_short})[/dim] [bold]>[/bold]"
            else:
                prompt_text = "[bold cyan]Oops[/bold cyan] [bold]>[/bold]"
            
            user_input = Prompt.ask(prompt_text)
            
            if not user_input:
                continue
            
            # Handle commands
            if handle_command(user_input, session_manager, console):
                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                continue
            
            console.print()
            
            # Check if this is a new session (target URL provided)
            if not current_session or user_input.startswith("http"):
                # Create new session
                target = user_input
                session_id = session_manager.create_session(target, "Security assessment")
                console.print(f"[green]✓ New session created:[/green] [dim]{session_id}[/dim]")
                console.print()
                
                # Execute workflow phases
                # Phase 1: Scope
                def generate_scope(target, feedback=None):
                    prompt = f"Generate a scope.md file for security assessment of {target}."
                    if feedback:
                        prompt += f" User feedback: {feedback}"
                    with console.status("[cyan]Generating scope...[/cyan]"):
                        response = orchestrator(prompt)
                    return str(response)
                
                if not workflow_phases.execute_scope_phase(target, generate_scope):
                    console.print("[red]Scope phase failed. Session aborted.[/red]")
                    continue
                
                console.print()
                
                # Phase 2: Intel
                def run_recon():
                    with console.status("[blue]Running reconnaissance...[/blue]"):
                        prompt = f"Perform reconnaissance on {target} and return findings as dict"
                        response = orchestrator(prompt)
                    return {"findings": str(response)}
                
                def generate_intel(findings, feedback=None):
                    prompt = f"Generate intel.md based on these findings: {findings}"
                    if feedback:
                        prompt += f" User feedback: {feedback}"
                    with console.status("[blue]Generating intel...[/blue]"):
                        response = orchestrator(prompt)
                    return str(response)
                
                if not workflow_phases.execute_intel_phase(run_recon, generate_intel):
                    console.print("[red]Intel phase failed. Session aborted.[/red]")
                    continue
                
                console.print()
                
                # Phase 3: Plan
                def generate_plan(intel, feedback=None):
                    prompt = f"Generate plan.md with checklist based on intel: {intel}"
                    if feedback:
                        prompt += f" User feedback: {feedback}"
                    with console.status("[magenta]Generating plan...[/magenta]"):
                        response = orchestrator(prompt)
                    return str(response)
                
                if not workflow_phases.execute_plan_phase(generate_plan):
                    console.print("[red]Plan phase failed. Session aborted.[/red]")
                    continue
                
                console.print()
                
                # Phase 4: Execution
                def execute_item(item_text):
                    try:
                        with console.status(f"[green]Executing: {item_text}[/green]"):
                            response = orchestrator(f"Execute: {item_text}")
                        return (True, str(response))
                    except Exception as e:
                        return (False, str(e))
                
                workflow_phases.execute_execution_phase(execute_item)
                
                console.print()
                console.print(f"[bold green]✓ Assessment complete![/bold green]")
                console.print(f"[dim]Session:[/dim] {session_id}")
                console.print(f"[dim]Results:[/dim] ~/.oops/sessions/{session_id}/")
                console.print()
            
            else:
                # Continue with current session
                with console.status("[bold cyan]Processing...[/bold cyan]", spinner="dots"):
                    response = orchestrator(user_input)
                
                console.print(Markdown(str(response)))
                console.print()
        
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Interrupted. Type 'exit' to quit.[/bold yellow]")
            continue
        except Exception as e:
            console.print(f"\n[bold red]An error occurred:[/bold red] {e}")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            continue


if __name__ == "__main__":
    main()