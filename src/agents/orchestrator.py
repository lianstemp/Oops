from strands import Agent
from .scope_agent import scope_manager_tool
from .intel_agent import intel_gatherer_tool
from .plan_agent import strategy_planner_tool
from ..config import get_model

def get_orchestrator():
    """
    Returns the configured Orchestrator Agent.
    """
    orchestrator_prompt = """
    You are the "Oops" Red Team Orchestrator. You are a high-end, autonomous cyber security agent.
    
    You have access to 3 specialized tools (which are actually other agents):
    1. `scope_manager_tool`: Use this FIRST to define the ROE and targets.
    2. `intel_gatherer_tool`: Use this SECOND to gather intelligence on the targets.
    3. `strategy_planner_tool`: Use this THIRD to create an attack plan.
    
    **Workflow Rule**:
    You MUST execute these strictly in order: Scope -> Intel -> Plan.
    Do NOT skip steps. Do NOT hallucinate data. Rely on the tools to generate the files.
    
    After using all tools and confirming the plan is generated, give a final summary to the user.
    """
    
    orchestrator = Agent(
        name="OopsOrchestrator",
        model=get_model(),
        system_prompt=orchestrator_prompt,
        tools=[scope_manager_tool, intel_gatherer_tool, strategy_planner_tool]
    )
    
    return orchestrator
