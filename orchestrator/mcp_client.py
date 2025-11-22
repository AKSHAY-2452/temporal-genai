"""
MCP Client to fetch available tools from the MCP server.
In production, this would connect to the actual MCP server.
"""

def get_tools():
    """
    Returns list of available MCP tools with their signatures.
    This is a simplified version - in production, fetch from MCP server.
    """
    return [
        {
            "name": "send_email",
            "description": "Sends email to a user",
            "params": {
                "to": "string - recipient email",
                "subject": "string - email subject",
                "body": "string - email body"
            }
        },
        {
            "name": "fetch_order",
            "description": "Fetch order details from system",
            "params": {
                "order_id": "string - unique order ID"
            }
        },
        {
            "name": "save_to_db",
            "description": "Saves data to database",
            "params": {
                "table": "string - table name",
                "data": "dict - data to save"
            }
        }
    ]

def get_tools_prompt():
    """Format tools for LLM prompt."""
    tools = get_tools()
    formatted = []
    for tool in tools:
        params_str = "\n    ".join([f"{k}: {v}" for k, v in tool["params"].items()])
        formatted.append(f"""
Tool: {tool["name"]}
Description: {tool["description"]}
Parameters:
    {params_str}
""")
    return "\n".join(formatted)