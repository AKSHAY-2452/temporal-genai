from temporalio import activity
from typing import Any, Dict

@activity.defn
async def fetch_order_activity(order_id: str) -> Dict:
    """
    Fetches an order by ID using the MCP tool.
    
    Args:
    order_id (str): The unique order ID.
    
    Returns:
    Dict: The order details.
    """
    try:
        # Call MCP tool
        result = fetch_order(order_id)
        return result
    except Exception as e:
        # Handle error
        raise activity.ApplicationError(f"Failed to fetch order: {str(e)}")

@activity.defn
async def send_email_activity(to: str, subject: str, body: str) -> Dict:
    """
    Sends a confirmation email to the customer using the MCP tool.
    
    Args:
    to (str): The recipient email.
    subject (str): The email subject.
    body (str): The email body.
    
    Returns:
    Dict: The email sending result.
    """
    try:
        # Call MCP tool
        result = send_email(to, subject, body)
        return result
    except Exception as e:
        # Handle error
        raise activity.ApplicationError(f"Failed to send email: {str(e)}")

@activity.defn
async def save_to_db_activity(table: str, data: Dict) -> Dict:
    """
    Saves the order status to the database using the MCP tool.
    
    Args:
    table (str): The table name.
    data (Dict): The data to save.
    
    Returns:
    Dict: The saving result.
    """
    try:
        # Call MCP tool
        result = save_to_db(table, data)
        return result
    except Exception as e:
        # Handle error
        raise activity.ApplicationError(f"Failed to save to database: {str(e)}")