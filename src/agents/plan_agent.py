from strands import Agent, tool
from tools.file_ops import read_file, write_file
from ..config import get_model

@tool
def strategy_planner_tool(query: str) -> str:
    """
    Creates an attack strategy based on gathered Intelligence.
    This tool should only be called AFTER intel_gatherer_tool.
    
    Args:
        query: Instruction to plan the attack.
    """
    plan_prompt = """
    You are the Strategy Planner Agent. Your job is to create a specific attack Plan based on 'intel.md'.
    
    1. First, use `read_file` to read 'intel.md'.
    2. Analyze the vulnerabilities found.
    3. Generate a 'plan.md' that details:
       - **Attack Vectors**: Specific methods to exploit the findings.
       - **Payloads**: Recommended payloads or tools to use.
       - **Kill Chain**: Step-by-step execution path.
       
    4. Use `write_file` to save this as 'plan.md'.
    """
    
    agent = Agent(
        name="StrategyPlanner",
        model=get_model(),
        system_prompt=plan_prompt,
        tools=[read_file, write_file]
    )
    
    response = agent.run(query)
    return response.text
