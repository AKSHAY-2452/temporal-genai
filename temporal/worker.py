"""
Temporal Worker that loads and runs dynamically generated workflows.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from temporalio.client import Client
from temporalio.worker import Worker

# Import generated workflows and activities
try:
    from generated import workflow, activities
    print("✅ Successfully imported generated workflow and activities")
except ImportError as e:
    print(f"❌ Could not import generated code: {e}")
    print("Make sure you've run orchestrator/generator.py first")
    sys.exit(1)

async def main():
    """Start the Temporal worker."""
    print("🔌 Connecting to Temporal server...")
    client = await Client.connect("localhost:7233")
    print("✅ Connected to Temporal")
    
    # Get all workflow and activity classes
    workflow_classes = [
        cls for name, cls in workflow.__dict__.items()
        if hasattr(cls, '__temporal_workflow_definition')
    ]
    
    activity_functions = [
        func for name, func in activities.__dict__.items()
        if hasattr(func, '__temporal_activity_definition')
    ]
    
    print(f"📋 Found {len(workflow_classes)} workflow(s)")
    print(f"📋 Found {len(activity_functions)} activity(ies)")
    
    print("🏃 Starting worker on task queue 'genai'...")
    worker = Worker(
        client,
        task_queue="genai",
        workflows=workflow_classes,
        activities=activity_functions,
    )
    
    print("✅ Worker started successfully!")
    print("⏳ Waiting for workflows...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())