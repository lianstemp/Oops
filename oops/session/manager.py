"""Session management for Oops.

Handles creation, loading, and management of assessment sessions.
Each session has a unique UUID and contains scope, intel, plan, and findings.
"""

import os
import uuid
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List


class SessionManager:
    """Manages assessment sessions with UUID-based isolation."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize session manager.
        
        Args:
            storage_path: Base path for session storage (default: ~/.oops/sessions)
        """
        if storage_path:
            self.storage_path = Path(storage_path).expanduser()
        else:
            self.storage_path = Path.home() / ".oops" / "sessions"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.current_session_id: Optional[str] = None
    
    def create_session(self, target: str, description: str = "") -> str:
        """Create a new session with unique UUID.
        
        Args:
            target: Target URL or domain
            description: Optional session description
        
        Returns:
            Session UUID
        """
        session_id = str(uuid.uuid4())
        session_path = self.storage_path / session_id
        session_path.mkdir(parents=True, exist_ok=True)
        
        # Create metadata
        metadata = {
            "session_id": session_id,
            "target": target,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "phase": "scope",
            "scope_approved": False,
            "intel_approved": False,
            "plan_approved": False,
        }
        
        self._save_metadata(session_id, metadata)
        self.current_session_id = session_id
        
        return session_id
    
    def load_session(self, session_id: str) -> Dict[str, Any]:
        """Load session metadata.
        
        Args:
            session_id: Session UUID
        
        Returns:
            Session metadata dictionary
        """
        metadata_path = self.storage_path / session_id / "metadata.json"
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Session {session_id} not found")
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        self.current_session_id = session_id
        return metadata
    
    def get_session_path(self, session_id: Optional[str] = None) -> Path:
        """Get path to session directory.
        
        Args:
            session_id: Session UUID (uses current if None)
        
        Returns:
            Path to session directory
        """
        sid = session_id or self.current_session_id
        if not sid:
            raise ValueError("No active session")
        
        return self.storage_path / sid
    
    def update_metadata(self, updates: Dict[str, Any], session_id: Optional[str] = None):
        """Update session metadata.
        
        Args:
            updates: Dictionary of fields to update
            session_id: Session UUID (uses current if None)
        """
        sid = session_id or self.current_session_id
        if not sid:
            raise ValueError("No active session")
        
        metadata = self.load_session(sid)
        metadata.update(updates)
        metadata["updated_at"] = datetime.now().isoformat()
        
        self._save_metadata(sid, metadata)
    
    def list_sessions(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """List all sessions.
        
        Args:
            active_only: Only return active sessions
        
        Returns:
            List of session metadata dictionaries
        """
        sessions = []
        
        for session_dir in self.storage_path.iterdir():
            if not session_dir.is_dir():
                continue
            
            metadata_path = session_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            if active_only and metadata.get("status") != "active":
                continue
            
            sessions.append(metadata)
        
        # Sort by creation time (newest first)
        sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return sessions
    
    def cleanup_old_sessions(self, days: int = 7):
        """Delete sessions older than specified days.
        
        Args:
            days: Number of days to keep sessions
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        for session_dir in self.storage_path.iterdir():
            if not session_dir.is_dir():
                continue
            
            metadata_path = session_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            created_at = datetime.fromisoformat(metadata.get("created_at", ""))
            
            if created_at < cutoff:
                # Delete session directory
                import shutil
                shutil.rmtree(session_dir)
    
    def _save_metadata(self, session_id: str, metadata: Dict[str, Any]):
        """Save session metadata to file.
        
        Args:
            session_id: Session UUID
            metadata: Metadata dictionary
        """
        metadata_path = self.storage_path / session_id / "metadata.json"
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_current_session(self) -> Optional[str]:
        """Get current session ID.
        
        Returns:
            Current session UUID or None
        """
        return self.current_session_id
    
    def set_current_session(self, session_id: str):
        """Set current session.
        
        Args:
            session_id: Session UUID
        """
        # Verify session exists
        self.load_session(session_id)
        self.current_session_id = session_id
