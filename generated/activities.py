from temporalio import activity
from typing import Any, Dict, List, Optional

@activity.defn
async def charge_card_activity(amount: float) -> Dict:
    try:
        # Simulating a card charge activity
        return {"status": "charged", "amount": amount}
    except Exception as e:
        raise RuntimeError(f"Activity failed: {e}")

@activity.defn
async def send_email_activity(to: str, subject: str, body: str) -> Dict:
    try:
        # Simulating an email send activity
        return {"status": "sent", "to": to, "subject": subject, "body": body}
    except Exception as e:
        raise RuntimeError(f"Activity failed: {e}")

@activity.defn
async def wait_activity(duration: int) -> Dict:
    try:
        # Simulating a wait activity
        import time
        time.sleep(duration * 3600)  # Convert hours to seconds
        return {"status": "waited", "duration": duration}
    except Exception as e:
        raise RuntimeError(f"Activity failed: {e}")