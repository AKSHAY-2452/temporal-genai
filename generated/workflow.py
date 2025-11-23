from temporalio import workflow
from datetime import timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional
from . import activities

@dataclass
class OrderProcessorInput:
    order_id: str
    customer_email: Optional[str] = None
    items: Optional[List[Dict]] = None

@workflow.defn
class OrderProcessor:
    @workflow.run
    async def run(self, input: OrderProcessorInput) -> Dict:
        try:
            # Charge the card
            charge_result = await workflow.execute_activity(
                activities.charge_card_activity,
                100.0,  # Hardcoded amount for demonstration
                start_to_close_timeout=timedelta(minutes=5),
            )
            
            # Send an email
            email_result = await workflow.execute_activity(
                activities.send_email_activity,
                input.customer_email if input.customer_email else "default@example.com",
                "Order Confirmation",
                "Your order has been processed.",
                start_to_close_timeout=timedelta(minutes=5),
            )
            
            # Wait for 1 hour
            wait_result = await workflow.execute_activity(
                activities.wait_activity,
                1,  # Wait for 1 hour
                start_to_close_timeout=timedelta(hours=1),
            )
            
            return {"status": "ok", "charge_result": charge_result, "email_result": email_result, "wait_result": wait_result}
        except Exception as e:
            raise workflow.ApplicationError(str(e))