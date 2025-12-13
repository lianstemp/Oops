from strands import Agent
from oops.config import get_model
from oops.tools.session_tools import (
    write_file,
    read_file,
    list_files,
    append_to_log,
    update_checklist_item,
    get_checklist_progress
)

def get_orchestrator():
    """
    Returns the configured Orchestrator Agent with session-aware tools.
    """
    orchestrator_prompt = """
    You are the "Oops" Red Team Orchestrator - an autonomous cyber security assessment agent.
    
    You are working within a session-based workflow where the user has already approved:
    - scope.md (Rules of Engagement)
    - intel.md (Reconnaissance findings)
    - plan.md (Attack plan with checklist)
    
    Your role is to:
    1. Generate content when requested (scope, intel, plan)
    2. Execute attack plan items
    3. Update progress in checklists
    4. Log all activities
    
    **Available Tools:**
    - write_file: Write content to session files
    - read_file: Read session files
    - list_files: List all session files
    - append_to_log: Log activities
    - update_checklist_item: Mark checklist items as complete
    - get_checklist_progress: Check progress
    
    **Guidelines:**
    - When generating scope.md: Include target, objectives, and restrictions
    - When generating intel.md: Include findings from reconnaissance
    - When generating plan.md: Use checklist format with `- [ ]` items
    - When executing: Update checklists with `update_checklist_item`
    - Always log important activities
    
    Be professional, thorough, and security-focused.
    """
    
    orchestrator = Agent(
        name="OopsOrchestrator",
        model=get_model(),
        system_prompt=orchestrator_prompt,
        tools=[
            write_file,
            read_file,
            list_files,
            append_to_log,
            update_checklist_item,
            get_checklist_progress
        ]
    )
    
    return orchestrator
