from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("business-tools")

@mcp.tool()
def send_email(to: str, subject: str, body: str):
    """
    Sends email to a user.
    Args:
        to: Email recipient
        subject: Email subject line
        body: Email body content
    """
    print(f"📧 Sending email to {to}: {subject}")
    return {"status": "sent", "to": to, "subject": subject}

@mcp.tool()
def fetch_order(order_id: str):
    """
    Fetch order details from system.
    Args:
        order_id: Unique order identifier
    """
    print(f"📦 Fetching order: {order_id}")
    return {
        "order_id": order_id, 
        "amount": 1200, 
        "status": "confirmed",
        "customer": "john@example.com"
    }

@mcp.tool()
def save_to_db(table: str, data: dict):
    """
    Saves data to database table.
    Args:
        table: Target table name
        data: Dictionary of data to save
    """
    print(f"💾 Saving to {table}: {data}")
    return {"status": "saved", "table": table, "record_id": "rec_123"}

if __name__ == "__main__":
    print("🚀 Starting MCP Tool Server...")
    mcp.run()