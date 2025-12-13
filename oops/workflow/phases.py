"""Workflow phase handlers for Oops assessment.

Manages the Scope → Intel → Plan → Execution workflow with approval gates.
"""

from typing import Optional, Dict, Any
from rich.console import Console
from .approval import ApprovalWorkflow
from ..session import SessionManager, SessionStorage


class WorkflowPhases:
    """Handles workflow phases with approval gates."""
    
    def __init__(
        self,
        session_manager: SessionManager,
        approval_workflow: ApprovalWorkflow
    ):
        """Initialize workflow phases.
        
        Args:
            session_manager: Session manager instance
            approval_workflow: Approval workflow instance
        """
        self.session_manager = session_manager
        self.approval = approval_workflow
        self.console = Console()
    
    def execute_scope_phase(
        self,
        target: str,
        generate_scope_fn: callable
    ) -> bool:
        """Execute scope definition phase.
        
        Args:
            target: Target URL/domain
            generate_scope_fn: Function to generate scope content
                              Should accept (target, feedback=None) and return str
        
        Returns:
            True if scope approved, False otherwise
        """
        self.approval.show_progress("scope", "Defining scope and Rules of Engagement...")
        
        session_id = self.session_manager.get_current_session()
        storage = SessionStorage(self.session_manager.get_session_path(session_id))
        
        feedback = None
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            # Generate scope content
            self.console.print(f"[dim]Generating scope.md (attempt {attempt}/{max_attempts})...[/dim]")
            scope_content = generate_scope_fn(target, feedback)
            
            # Request approval
            approved, feedback = self.approval.request_approval(
                scope_content,
                "scope.md",
                "scope"
            )
            
            if approved:
                # Save scope
                storage.save_scope(scope_content)
                storage.append_log(f"Scope approved for target: {target}")
                
                # Update metadata
                self.session_manager.update_metadata({
                    "scope_approved": True,
                    "phase": "intel"
                })
                
                self.approval.show_success("Scope approved and saved")
                return True
            else:
                self.approval.show_warning(f"Scope rejected. Regenerating with feedback...")
                storage.append_log(f"Scope rejected. Feedback: {feedback}")
        
        self.approval.show_error("Max attempts reached. Scope not approved.")
        return False
    
    def execute_intel_phase(
        self,
        run_recon_fn: callable,
        generate_intel_fn: callable
    ) -> bool:
        """Execute intelligence gathering phase.
        
        Args:
            run_recon_fn: Function to run reconnaissance
                         Should return dict of findings
            generate_intel_fn: Function to generate intel content
                              Should accept (findings, feedback=None) and return str
        
        Returns:
            True if intel approved, False otherwise
        """
        self.approval.show_progress("intel", "Gathering intelligence...")
        
        session_id = self.session_manager.get_current_session()
        storage = SessionStorage(self.session_manager.get_session_path(session_id))
        
        # Run reconnaissance
        self.console.print("[dim]Running reconnaissance tools...[/dim]")
        findings = run_recon_fn()
        storage.append_log(f"Reconnaissance complete. Findings: {len(findings)} items")
        
        feedback = None
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            # Generate intel content
            self.console.print(f"[dim]Generating intel.md (attempt {attempt}/{max_attempts})...[/dim]")
            intel_content = generate_intel_fn(findings, feedback)
            
            # Request approval
            approved, feedback = self.approval.request_approval(
                intel_content,
                "intel.md",
                "intel"
            )
            
            if approved:
                # Save intel
                storage.save_intel(intel_content)
                storage.append_log("Intel approved")
                
                # Update metadata
                self.session_manager.update_metadata({
                    "intel_approved": True,
                    "phase": "plan"
                })
                
                self.approval.show_success("Intel approved and saved")
                return True
            else:
                self.approval.show_warning("Intel rejected. Regenerating with feedback...")
                storage.append_log(f"Intel rejected. Feedback: {feedback}")
        
        self.approval.show_error("Max attempts reached. Intel not approved.")
        return False
    
    def execute_plan_phase(
        self,
        generate_plan_fn: callable
    ) -> bool:
        """Execute attack planning phase.
        
        Args:
            generate_plan_fn: Function to generate plan content with checklist
                             Should accept (intel, feedback=None) and return str
        
        Returns:
            True if plan approved, False otherwise
        """
        self.approval.show_progress("plan", "Creating attack plan...")
        
        session_id = self.session_manager.get_current_session()
        storage = SessionStorage(self.session_manager.get_session_path(session_id))
        
        # Load intel for context
        intel_content = storage.load_intel()
        
        feedback = None
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            # Generate plan content
            self.console.print(f"[dim]Generating plan.md with checklist (attempt {attempt}/{max_attempts})...[/dim]")
            plan_content = generate_plan_fn(intel_content, feedback)
            
            # Request approval
            approved, feedback = self.approval.request_approval(
                plan_content,
                "plan.md",
                "plan"
            )
            
            if approved:
                # Save plan
                storage.save_plan(plan_content)
                storage.append_log("Plan approved")
                
                # Update metadata
                self.session_manager.update_metadata({
                    "plan_approved": True,
                    "phase": "execution"
                })
                
                self.approval.show_success("Plan approved and saved")
                return True
            else:
                self.approval.show_warning("Plan rejected. Regenerating with feedback...")
                storage.append_log(f"Plan rejected. Feedback: {feedback}")
        
        self.approval.show_error("Max attempts reached. Plan not approved.")
        return False
    
    def execute_execution_phase(
        self,
        execute_item_fn: callable
    ) -> bool:
        """Execute attack plan items.
        
        Args:
            execute_item_fn: Function to execute a plan item
                            Should accept (item_text) and return (success, output)
        
        Returns:
            True if execution completed, False otherwise
        """
        self.approval.show_progress("execution", "Executing attack plan...")
        
        session_id = self.session_manager.get_current_session()
        storage = SessionStorage(self.session_manager.get_session_path(session_id))
        
        # Get checklist items
        items = storage.get_checklist_items()
        
        if not items:
            self.approval.show_warning("No checklist items found in plan")
            return False
        
        total = len(items)
        completed_count = 0
        
        for i, (already_done, item_text) in enumerate(items, 1):
            if already_done:
                self.console.print(f"[dim][{i}/{total}] Skipping (already done): {item_text}[/dim]")
                completed_count += 1
                continue
            
            self.console.print(f"[cyan][{i}/{total}][/cyan] Executing: {item_text}")
            storage.append_log(f"Executing: {item_text}")
            
            # Execute item
            success, output = execute_item_fn(item_text)
            
            if success:
                # Mark as completed
                storage.update_checklist(item_text, completed=True)
                storage.append_log(f"✓ Completed: {item_text}")
                self.approval.show_success(f"Completed: {item_text}")
                completed_count += 1
            else:
                storage.append_log(f"✗ Failed: {item_text} - {output}")
                self.approval.show_error(f"Failed: {item_text}")
        
        # Show final progress
        self.console.print()
        self.console.print(f"[bold]Execution complete: {completed_count}/{total} items completed[/bold]")
        
        # Update metadata
        self.session_manager.update_metadata({
            "phase": "completed",
            "status": "completed"
        })
        
        return True
