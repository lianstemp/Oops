from strands import Agent, tool
from oops.tools.session_tools import write_file
from oops.config import get_model
import dns.resolver
import socket
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def resolve_domain(domain: str) -> dict:
    """
    Resolves a domain name to its IP addresses.
    """
    results = {"A": [], "MX": [], "NS": []}
    try:
        # A Records
        try:
            answers = dns.resolver.resolve(domain, 'A')
            results["A"] = [r.to_text() for r in answers]
        except Exception:
            pass

        # MX Records
        try:
            answers = dns.resolver.resolve(domain, 'MX')
            results["MX"] = [r.to_text() for r in answers]
        except Exception:
            pass
            
        # NS Records
        try:
            answers = dns.resolver.resolve(domain, 'NS')
            results["NS"] = [r.to_text() for r in answers]
        except Exception:
            pass

    except Exception as e:
        logger.error(f"Error resolving domain {domain}: {e}")
        return {"error": str(e)}
    
    return results

@tool
def scope_manager_tool(query: str) -> str:
    """
    Defines the Rules of Engagement and validates the target.
    REAL implementation: Resolves DNS to ensure target exists.
    
    Args:
        query: The user's initial request or scope description.
    """
    # Simple extraction (in a real agent, the LLM would extract this, but here we can helper-function it or let LLM do it)
    # For this architecture, we let the LLM use the tool, so we need to inject the validation capability into the prompt context
    # or expose a sub-tool. 
    # To keep it simple for "Agents as Tools": The Scope Agent IS the tool. 
    # It will use python Logic inside to validate.
    
    scope_prompt = """
    You are the Scope Manager Agent. Your job is to define the ROE.
    
    1. EXTRACT the target domain from the user's query.
    2. I (the system) will provide you with DNS resolution data for the target if you identify one.
    3. Generate 'scope.md' containing:
       - **Target**: Domain and resolved IPs.
       - **Limits**: Strictly NO denial of service.
       - **Permissions**: Authorized for assessment.
    
    Use the `write_file` tool to save 'scope.md'.
    """
    
    # We can pre-process to help the agent or just give it the capabilities. 
    # A better pattern: The Agent has a `validate_target` tool it can call.
    
    @tool
    def validate_target(domain: str) -> str:
        """
        Validates a target domain by performing DNS resolution.
        """
        info = resolve_domain(domain)
        return f"DNS Info for {domain}: {info}"

    agent = Agent(
        name="ScopeManager",
        model=get_model(),
        system_prompt=scope_prompt,
        tools=[write_file, validate_target]
    )
    
    response = agent(query)
    return str(response)
