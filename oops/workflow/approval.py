"""User approval workflow for MD files.

Handles displaying MD content and requesting user approval with feedback support.
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from typing import Tuple, Optional


class ApprovalWorkflow:
    """Manages user approval for generated MD files."""
    
    def __init__(self):
        """Initialize approval workflow."""
        self.console = Console()
    
    def request_approval(
        self,
        content: str,
        title: str,
        phase: str
    ) -> Tuple[bool, Optional[str]]:
        """Request user approval for MD content.
        
        Args:
            content: Markdown content to display
            title: Title for the panel
            phase: Phase name (scope/intel/plan)
        
        Returns:
            Tuple of (approved, feedback)
            - approved: True if user approved, False otherwise
            - feedback: User feedback if rejected, None if approved
        """
        # Display content in a panel
        self.console.print()
        self.console.print(Panel(
            Markdown(content),
            title=f"[bold cyan]{title}[/bold cyan]",
            border_style="cyan",
            expand=False
        ))
        self.console.print()
        
        # Request approval
        while True:
            choice = Prompt.ask(
                f"[bold]Approve this {phase}?[/bold]",
                choices=["y", "n", "edit", "view"],
                default="y"
            )
            
            if choice == "y":
                return (True, None)
            
            elif choice == "n":
                # Request feedback
                feedback = Prompt.ask(
                    "[yellow]What would you like to change?[/yellow]"
                )
                return (False, feedback)
            
            elif choice == "edit":
                # Show edit instructions
                self.console.print(
                    "[yellow]To edit, provide feedback and the AI will regenerate.[/yellow]"
                )
                feedback = Prompt.ask(
                    "[yellow]What would you like to change?[/yellow]"
                )
                return (False, feedback)
            
            elif choice == "view":
                # Re-display content
                self.console.print()
                self.console.print(Panel(
                    Markdown(content),
                    title=f"[bold cyan]{title}[/bold cyan]",
                    border_style="cyan",
                    expand=False
                ))
                self.console.print()
    
    def show_progress(self, phase: str, message: str):
        """Show progress message.
        
        Args:
            phase: Current phase
            message: Progress message
        """
        phase_colors = {
            "scope": "cyan",
            "intel": "blue",
            "plan": "magenta",
            "execution": "green"
        }
        
        color = phase_colors.get(phase, "white")
        self.console.print(f"[{color}][{phase.upper()}][/{color}] {message}")
    
    def show_error(self, message: str):
        """Show error message.
        
        Args:
            message: Error message
        """
        self.console.print(f"[bold red]✗ Error:[/bold red] {message}")
    
    def show_success(self, message: str):
        """Show success message.
        
        Args:
            message: Success message
        """
        self.console.print(f"[bold green]✓[/bold green] {message}")
    
    def show_warning(self, message: str):
        """Show warning message.
        
        Args:
            message: Warning message
        """
        self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")
    
    def confirm_action(self, message: str, default: bool = False) -> bool:
        """Request confirmation for an action.
        
        Args:
            message: Confirmation message
            default: Default choice
        
        Returns:
            True if confirmed, False otherwise
        """
        return Confirm.ask(message, default=default)
