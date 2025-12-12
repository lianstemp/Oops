from strands import Agent, tool
from tools.file_ops import read_file, write_file
from ..config import get_model

@tool
def intel_gatherer_tool(query: str) -> str:
    """
    Performs reconnaissance based on the defined Scope.
    This tool should only be called AFTER scope_manager_tool.
    
    Args:
        query: Instruction to gather intel.
    """
    intel_prompt = """
    You are the Intel Gatherer Agent. Your job is to simulate reconnaissance on the targets defined in 'scope.md'.
    
    1. First, use `read_file` to read 'scope.md' to understand the targets and limits.
    2. Then, generate a simulated intelligence report 'intel.md' containing:
       - **Open Ports**: (e.g., 80, 443, 22).
       - **Tech Stack**: (e.g., Nginx, Python/Django, PostgreSQL).
       - **Potential Vulnerabilities**: (e.g., Outdated software versions, Misconfigurations).
       
       *Note: Do not actually scan the internet. Generate creating/realistic data for the purpose of this architectural demo.*
       
    3. Use `write_file` to save this as 'intel.md'.
    """
    
    agent = Agent(
        name="IntelGatherer",
        model=get_model(),
        system_prompt=intel_prompt,
        tools=[read_file, write_file]
    )
    
    response = agent.run(query)
    return response.text
