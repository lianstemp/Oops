"""Session-aware tool wrappers for Oops.

Wraps existing tools to automatically use session context and storage.
"""

from pathlib import Path
from typing import Optional
from strands.tools import tool
from ..session import SessionManager, SessionStorage


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def set_session_manager(manager: SessionManager):
    """Set the global session manager.
    
    Args:
        manager: SessionManager instance
    """
    global _session_manager
    _session_manager = manager


def get_session_storage() -> Optional[SessionStorage]:
    """Get storage for current session.
    
    Returns:
        SessionStorage instance or None if no active session
    """
    if not _session_manager:
        return None
    
    session_id = _session_manager.get_current_session()
    if not session_id:
        return None
    
    session_path = _session_manager.get_session_path(session_id)
    return SessionStorage(session_path)


@tool
def write_file(filename: str, content: str) -> str:
    """Write content to a file in the current session.
    
    Args:
        filename: Name of the file (e.g., 'scope.md', 'intel.md', 'plan.md')
        content: Content to write
    
    Returns:
        Success message with file path
    """
    storage = get_session_storage()
    
    if not storage:
        # Fallback to output directory if no session
        output_path = Path("output") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(content)
        return f"File written to: {output_path}"
    
    # Write to session directory
    file_path = storage.session_path / filename
    with open(file_path, 'w') as f:
        f.write(content)
    
    storage.append_log(f"File written: {filename}")
    
    return f"File written to session: {filename}"


@tool
def read_file(filename: str) -> str:
    """Read content from a file in the current session.
    
    Args:
        filename: Name of the file to read
    
    Returns:
        File content
    """
    storage = get_session_storage()
    
    if not storage:
        # Fallback to output directory
        output_path = Path("output") / filename
        if not output_path.exists():
            return f"File not found: {filename}"
        
        with open(output_path, 'r') as f:
            return f.read()
    
    # Read from session directory
    file_path = storage.session_path / filename
    
    if not file_path.exists():
        return f"File not found: {filename}"
    
    with open(file_path, 'r') as f:
        return f.read()


@tool
def list_files() -> str:
    """List all files in the current session.
    
    Returns:
        List of files
    """
    storage = get_session_storage()
    
    if not storage:
        # Fallback to output directory
        output_path = Path("output")
        if not output_path.exists():
            return "No files found"
        
        files = [f.name for f in output_path.iterdir() if f.is_file()]
        return "\n".join(files) if files else "No files found"
    
    # List session files
    files = [f.name for f in storage.session_path.iterdir() if f.is_file()]
    return "\n".join(files) if files else "No files found"


@tool
def append_to_log(message: str) -> str:
    """Append a message to the session execution log.
    
    Args:
        message: Log message
    
    Returns:
        Success message
    """
    storage = get_session_storage()
    
    if not storage:
        return "No active session"
    
    storage.append_log(message)
    return "Message logged"


@tool
def update_checklist_item(item_text: str, completed: bool = True) -> str:
    """Update a checklist item in plan.md.
    
    Args:
        item_text: Text of the checklist item
        completed: Whether to mark as completed
    
    Returns:
        Success message
    """
    storage = get_session_storage()
    
    if not storage:
        return "No active session"
    
    storage.update_checklist(item_text, completed)
    return f"Checklist item updated: {item_text}"


@tool
def get_checklist_progress() -> str:
    """Get progress of checklist items in plan.md.
    
    Returns:
        Progress summary
    """
    storage = get_session_storage()
    
    if not storage:
        return "No active session"
    
    completed, total = storage.get_progress()
    
    if total == 0:
        return "No checklist items found"
    
    percentage = (completed / total) * 100
    return f"Progress: {completed}/{total} ({percentage:.1f}%)"
