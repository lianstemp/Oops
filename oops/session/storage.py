"""Storage operations for session artifacts.

Handles reading/writing MD files, updating checklists, and managing session artifacts.
"""

import re
from pathlib import Path
from typing import Optional, List, Tuple


class SessionStorage:
    """Handles file operations for session artifacts."""
    
    def __init__(self, session_path: Path):
        """Initialize storage for a session.
        
        Args:
            session_path: Path to session directory
        """
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
    
    def save_scope(self, content: str):
        """Save scope.md file.
        
        Args:
            content: Scope markdown content
        """
        scope_path = self.session_path / "scope.md"
        with open(scope_path, 'w') as f:
            f.write(content)
    
    def load_scope(self) -> Optional[str]:
        """Load scope.md file.
        
        Returns:
            Scope content or None if not exists
        """
        scope_path = self.session_path / "scope.md"
        if not scope_path.exists():
            return None
        
        with open(scope_path, 'r') as f:
            return f.read()
    
    def save_intel(self, content: str):
        """Save intel.md file.
        
        Args:
            content: Intel markdown content
        """
        intel_path = self.session_path / "intel.md"
        with open(intel_path, 'w') as f:
            f.write(content)
    
    def load_intel(self) -> Optional[str]:
        """Load intel.md file.
        
        Returns:
            Intel content or None if not exists
        """
        intel_path = self.session_path / "intel.md"
        if not intel_path.exists():
            return None
        
        with open(intel_path, 'r') as f:
            return f.read()
    
    def save_plan(self, content: str):
        """Save plan.md file with checklist.
        
        Args:
            content: Plan markdown content with checklist
        """
        plan_path = self.session_path / "plan.md"
        with open(plan_path, 'w') as f:
            f.write(content)
    
    def load_plan(self) -> Optional[str]:
        """Load plan.md file.
        
        Returns:
            Plan content or None if not exists
        """
        plan_path = self.session_path / "plan.md"
        if not plan_path.exists():
            return None
        
        with open(plan_path, 'r') as f:
            return f.read()
    
    def update_checklist(self, item_text: str, completed: bool = True):
        """Update a checklist item in plan.md.
        
        Args:
            item_text: Text of the checklist item to update
            completed: Whether to mark as completed (True) or uncompleted (False)
        """
        plan_content = self.load_plan()
        if not plan_content:
            return
        
        # Pattern to match checklist items
        # Matches: - [ ] item or - [x] item
        checkbox = "[x]" if completed else "[ ]"
        opposite_checkbox = "[ ]" if completed else "[x]"
        
        # Replace the specific item
        # Look for the item with either checkbox state
        pattern1 = re.compile(rf"^(\s*-\s*)\[ \](\s*{re.escape(item_text)})", re.MULTILINE)
        pattern2 = re.compile(rf"^(\s*-\s*)\[x\](\s*{re.escape(item_text)})", re.MULTILINE)
        
        updated_content = pattern1.sub(rf"\1{checkbox}\2", plan_content)
        updated_content = pattern2.sub(rf"\1{checkbox}\2", updated_content)
        
        self.save_plan(updated_content)
    
    def get_checklist_items(self) -> List[Tuple[bool, str]]:
        """Get all checklist items from plan.md.
        
        Returns:
            List of (completed, item_text) tuples
        """
        plan_content = self.load_plan()
        if not plan_content:
            return []
        
        items = []
        
        # Pattern to match checklist items
        pattern = re.compile(r"^\s*-\s*\[([ x])\]\s*(.+)$", re.MULTILINE)
        
        for match in pattern.finditer(plan_content):
            completed = match.group(1).lower() == 'x'
            item_text = match.group(2).strip()
            items.append((completed, item_text))
        
        return items
    
    def get_progress(self) -> Tuple[int, int]:
        """Get checklist progress.
        
        Returns:
            Tuple of (completed_count, total_count)
        """
        items = self.get_checklist_items()
        if not items:
            return (0, 0)
        
        completed = sum(1 for done, _ in items if done)
        total = len(items)
        
        return (completed, total)
    
    def save_findings(self, content: str):
        """Save findings.md file.
        
        Args:
            content: Findings markdown content
        """
        findings_path = self.session_path / "findings.md"
        with open(findings_path, 'w') as f:
            f.write(content)
    
    def load_findings(self) -> Optional[str]:
        """Load findings.md file.
        
        Returns:
            Findings content or None if not exists
        """
        findings_path = self.session_path / "findings.md"
        if not findings_path.exists():
            return None
        
        with open(findings_path, 'r') as f:
            return f.read()
    
    def append_log(self, message: str):
        """Append to execution.log file.
        
        Args:
            message: Log message to append
        """
        log_path = self.session_path / "execution.log"
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_path, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def load_log(self) -> str:
        """Load execution.log file.
        
        Returns:
            Log content or empty string if not exists
        """
        log_path = self.session_path / "execution.log"
        if not log_path.exists():
            return ""
        
        with open(log_path, 'r') as f:
            return f.read()
