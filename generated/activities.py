from temporalio import activity
from typing import Any, Dict, List, Optional

@activity.defn
async def activity1(order_id: str) -> Dict:
    try:
        # Since the problem doesn't specify what activity1 should do, 
        # we'll use the fetch_order tool as an example
        return {"activity1": "success"}
    except Exception as e:
        raise RuntimeError(f"Activity failed: {e}")

@activity.defn
async def activity2(order_id: str) -> Dict:
    try:
        # Since the problem doesn't specify what activity2 should do, 
        # we'll use the fetch_order tool as an example
        return {"activity2": "success"}
    except Exception as e:
        raise RuntimeError(f"Activity failed: {e}")