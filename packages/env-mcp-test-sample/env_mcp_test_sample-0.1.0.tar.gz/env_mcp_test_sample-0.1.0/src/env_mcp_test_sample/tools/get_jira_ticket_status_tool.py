import requests
from typing import Optional

def get_jira_ticket_status_tool(
    ticket_id: str,
    base_url: Optional[str] = None,
    api_token: Optional[str] = None,
    email: Optional[str] = None
) -> str:
    if not all([ticket_id, base_url, api_token, email]):
        return "❌ Missing required JIRA credentials or ticket ID."

    url = f"{base_url}/rest/api/3/issue/{ticket_id}"
    headers = {
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, auth=(email, api_token), headers=headers)
        if response.status_code == 200:
            data = response.json()
            status = data.get("fields", {}).get("status", {}).get("name")
            return f"✅ Ticket {ticket_id} status: {status}"
        else:
            return f"❌ Failed to fetch ticket. Status Code: {response.status_code}, Message: {response.text}"
    except Exception as e:
        return f"❌ Exception occurred: {e}"
