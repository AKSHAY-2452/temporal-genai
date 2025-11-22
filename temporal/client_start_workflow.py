"""
Client to start a Temporal workflow execution.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from temporalio.client import Client

# Import generated workflow
try:
    from generated import workflow
    print("✅ Successfully imported generated workflow")
except ImportError as e:
    print(f"❌ Could not import generated workflow: {e}")
    print("Make sure you've run orchestrator/generator.py first")
    sys.exit(1)

async def main():
    """Execute the generated workflow."""
    print("🔌 Connecting to Temporal server...")
    client = await Client.connect("localhost:7233")
    print("✅ Connected to Temporal")
    
    # Get the first workflow class (in real app, you'd specify which one)
    workflow_class = None
    for name, cls in workflow.__dict__.items():
        if hasattr(cls, '__temporal_workflow_definition'):
            workflow_class = cls
            break
    
    if not workflow_class:
        print("❌ No workflow class found in generated code")
        sys.exit(1)
    
    print(f"🚀 Starting workflow: {workflow_class.__name__}")
    
    # Example input - modify based on your workflow
    workflow_input = {
        "order_id": "ORD-123"
    }
    
    result = await client.execute_workflow(
        workflow_class.run,
        workflow_input,
        id=f"workflow-{workflow_class.__name__}-001",
        task_queue="genai",
    )
    
    print("\n✅ Workflow completed!")
    print(f"📊 Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())