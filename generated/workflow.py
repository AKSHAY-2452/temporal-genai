from temporalio import workflow
from datetime import timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional
from . import activities

@dataclass
class PaymentWorkflowInput:
    order_id: str
    customer_email: Optional[str] = None
    items: Optional[List[Dict]] = None

@workflow.defn
class PaymentWorkflow:
    @workflow.run
    async def run(self, input: PaymentWorkflowInput) -> Dict:
        try:
            result1 = await workflow.execute_activity(
                activities.activity1,
                input.order_id,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=workflow.RetryPolicy(
                    maximum_attempts=1,
                    backoff_coefficient=1,
                    initial_interval=timedelta(seconds=10),
                    maximum_interval=timedelta(seconds=10),
                    maximum_backoff_interval=timedelta(seconds=10),
                ),
            )
            result2 = await workflow.execute_activity(
                activities.activity2,
                input.order_id,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=workflow.RetryPolicy(
                    maximum_attempts=1,
                    backoff_coefficient=1,
                    initial_interval=timedelta(seconds=10),
                    maximum_interval=timedelta(seconds=10),
                    maximum_backoff_interval=timedelta(seconds=10),
                ),
            )
            return {"status": "ok", "data": {"activity1": result1, "activity2": result2}}
        except Exception as e:
            raise workflow.ApplicationError(str(e))