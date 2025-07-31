from mcp.server.fastmcp import FastMCP
from .tools.get_jira_ticket_status_tool import get_jira_ticket_status_tool
import os
import logging

mcp = FastMCP()

@mcp.tool() 
def get_jira_ticket_status(ticket_id: str, base_url: str = None, api_token: str = None, email: str = None) -> str:
    """
    Fetch the status of a JIRA ticket.
    
    Parameters:
    - ticket_id: ID of the JIRA ticket (e.g., "ABC-123").
    - base_url: Base URL of the JIRA instance (optional if JIRA_BASE_URL env var is set).
    - api_token: API token for JIRA authentication (optional if JIRA_API_TOKEN env var is set).
    - email: Email address associated with the JIRA account (optional if JIRA_EMAIL env var is set).
    """
    base_url = base_url or os.getenv("JIRA_BASE_URL")
    api_token = api_token or os.getenv("JIRA_API_TOKEN")
    email = email or os.getenv("JIRA_EMAIL")

    return get_jira_ticket_status_tool(ticket_id, base_url, api_token, email)

def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting MCP server...")
    mcp.run()