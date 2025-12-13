from strands import Agent, tool
from oops.tools.session_tools import read_file, write_file
from oops.config import get_model

@tool
def strategy_planner_tool(query: str) -> str:
    """
    Creates an attack strategy based on gathered Intelligence.
    Analyzes real headers and tech stack data to propose specific vectors.
    
    Args:
        query: Instruction to plan the attack.
    """
    plan_prompt = """
    You are the Strategy Planner Agent.
    
    1. Read 'intel.md' to see what was actually discovered.
    2. Analyze the 'Tech Stack' and 'Security Headers'.
    3. Generate 'plan.md' covering:
       - **Analysis**: Interpret the Server headers (e.g., "Apache 2.4.49 is vulnerable to Path Traversal").
       - **Vectors**: Map findings to specific attacks (e.g., "Missing X-Frame-Options -> Clickjacking").
       - **Tools**: Recommend tools for the specific findings (e.g., "Use Burp Suite for...").
       
       - **Plan**: A hierarchical checklist of actions.
         - Main phases must be top-level items: `- [ ] Phase Name`
         - Specific actions must be indented sub-items: `  - [ ] Action`
       
    Use `write_file` to save 'plan.md'.
    """
    
    agent = Agent(
        name="StrategyPlanner",
        model=get_model(),
        system_prompt=plan_prompt,
        tools=[read_file, write_file]
    )
    
    response = agent(query)
    return str(response)
