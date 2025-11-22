from temporalio import workflow
from datetime import timedelta
from dataclasses import dataclass
from typing import Dict
from . import activities

# -----------------------------
# Dataclasses for workflow IO
# -----------------------------
@dataclass
class OrderInput:
    order_id: str
    customer_email: str


@dataclass
class OrderResult:
    order_id: str
    status: str


# -----------------------------
# Workflow Definition
# -----------------------------
@workflow.defn
class OrderProcessingWorkflow:

    @workflow.run
    async def run(self, order: OrderInput) -> OrderResult:
        """
        Main workflow to process an order.
        Steps:
        1. Fetch order data.
        2. Send confirmation email.
        3. Save confirmation status in DB.
        """

        try:
            # 1️⃣ Fetch order info
            fetched_order = await workflow.execute_activity(
                activities.fetch_order_activity,
                order.order_id,
                start_to_close_timeout=timedelta(minutes=5),
            )

            # 2️⃣ Send confirmation email
            await workflow.execute_activity(
                activities.send_email_activity,
                order.customer_email,
                "Order Confirmation",
                f"Your order {order.order_id} has been confirmed.",
                start_to_close_timeout=timedelta(minutes=5),
            )

            # 3️⃣ Save new order status
            await workflow.execute_activity(
                activities.save_to_db_activity,
                "orders",
                {"order_id": order.order_id, "status": "confirmed"},
                start_to_close_timeout=timedelta(minutes=5),
            )

            # 4️⃣ Final structured result
            return OrderResult(order_id=order.order_id, status="confirmed")

        except Exception as e:
            raise workflow.ApplicationError(
                f"Failed to process order: {str(e)}"
            )
