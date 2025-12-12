from strands import Agent, tool
from tools.file_ops import write_file
from ..config import get_model

@tool
def scope_manager_tool(query: str) -> str:
    """
    Defines the Rules of Engagement based on the user's request.
    This tool should be called to establish the scope of the assessment.
    
    Args:
        query: The user's initial request or scope description.
    """
    scope_prompt = """
    You are the Scope Manager Agent. Your ONE job is to strictly define the Rules of Engagement (ROE) for a security assessment.
    
    You do NOT perform attacks. You do NOT scan. You only PLAN the scope.
    
    Take the user's input and generate a strictly formatted markdown document 'scope.md'.
    The document MUST contain:
    1. **Target**: The specific domains/IPs in scope.
    2. **Limits**: What is OUT of scope (e.g., "Do not attack production databases").
    3. **Permissions**: A statement confirming authorization (simulated for this context).
    
    Use the `write_file` tool to save this as 'scope.md'.
    """
    
    agent = Agent(
        name="ScopeManager",
        model=get_model(),
        system_prompt=scope_prompt,
        tools=[write_file]
    )
    
    response = agent.run(query)
    return response.text
