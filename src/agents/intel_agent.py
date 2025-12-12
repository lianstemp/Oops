from strands import Agent, tool
from tools.file_ops import read_file, write_file
from config import get_model
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def intel_gatherer_tool(query: str) -> str:
    """
    Performs real reconnaissance using HTTP requests.
    """
    
    @tool
    def scan_headers(url: str) -> str:
        """
        Fetches HTTP headers to identify server technologies.
        Args:
            url: The URL to scan (must include http:// or https://)
        """
        try:
            # Enforce schema if missing
            if not url.startswith("http"):
                url = "https://" + url
                
            response = requests.head(url, timeout=5)
            headers = dict(response.headers)
            
            # Basic analysis
            server = headers.get("Server", "Unknown")
            powered_by = headers.get("X-Powered-By", "Unknown")
            
            return f"URL: {url}\nStatus: {response.status_code}\nServer: {server}\nX-Powered-By: {powered_by}\nFull Headers: {headers}"
        except Exception as e:
            return f"Error scanning {url}: {str(e)}"

    intel_prompt = """
    You are the Intel Gatherer Agent.
    
    1. Read 'scope.md' to get the target.
    2. Use `scan_headers` to fingerprint the web server.
    3. Generate 'intel.md' with:
       - **Live Assets**: Which URLs responded.
       - **Tech Stack**: Server version, backend technologies (from headers).
       - **Security Headers**: Missing headers like X-Frame-Options, HSTS, etc.
       
    Use `write_file` to save 'intel.md'.
    """
    
    agent = Agent(
        name="IntelGatherer",
        model=get_model(),
        system_prompt=intel_prompt,
        tools=[read_file, write_file, scan_headers]
    )
    
    response = agent(query)
    return str(response)
