"""
Main code generator that orchestrates the LLM-based workflow creation.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.llm_client import generate_code
from orchestrator.mcp_client import get_tools_prompt

def load_prompt_template():
    """Load the prompt template."""
    template_path = Path(__file__).parent / "prompts" / "generate_code_prompt.txt"
    with open(template_path, "r") as f:
        return f.read()

def parse_generated_code(code: str) -> tuple[str, str]:
    """
    Parse LLM output to extract activities and workflow code.
    
    Returns:
        tuple of (activities_code, workflow_code)
    """
    try:
        # Extract activities
        act_start = code.find("### ACTIVITIES_START ###")
        act_end = code.find("### ACTIVITIES_END ###")
        activities = code[act_start + len("### ACTIVITIES_START ###"):act_end].strip()
        
        # Extract workflow
        wf_start = code.find("### WORKFLOW_START ###")
        wf_end = code.find("### WORKFLOW_END ###")
        workflow = code[wf_start + len("### WORKFLOW_START ###"):wf_end].strip()
        
        # Clean up markdown code blocks if present
        activities = activities.replace("```python", "").replace("```", "").strip()
        workflow = workflow.replace("```python", "").replace("```", "").strip()
        
        return activities, workflow
    except Exception as e:
        print(f"❌ Error parsing generated code: {e}")
        print("Generated code:")
        print(code)
        raise

def save_generated_files(activities_code: str, workflow_code: str):
    """Save generated code to files."""
    generated_dir = Path(__file__).parent.parent / "generated"
    generated_dir.mkdir(exist_ok=True)
    
    # Create __init__.py if it doesn't exist
    init_file = generated_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("")
    
    # Save activities
    activities_file = generated_dir / "activities.py"
    activities_file.write_text(activities_code)
    print(f"✅ Generated: {activities_file}")
    
    # Save workflow
    workflow_file = generated_dir / "workflow.py"
    workflow_file.write_text(workflow_code)
    print(f"✅ Generated: {workflow_file}")

def generate_temporal_code(user_instruction: str):
    """
    Main function to generate Temporal workflow and activities.
    
    Args:
        user_instruction: Natural language description of what to build
    """
    print("🤖 Starting code generation...")
    print(f"📝 Instruction: {user_instruction}")
    
    # Get available tools
    print("🔧 Fetching available MCP tools...")
    tools_description = get_tools_prompt()
    
    # Load and format prompt
    print("📄 Building prompt...")
    template = load_prompt_template()
    prompt = template.format(
        user_instruction=user_instruction,
        tools=tools_description
    )
    
    # Generate code
    print("🧠 Calling LLM to generate code...")
    generated_code = generate_code(prompt)
    
    # Parse and save
    print("📦 Parsing generated code...")
    activities, workflow = parse_generated_code(generated_code)
    
    print("💾 Saving files...")
    save_generated_files(activities, workflow)
    
    print("\n✨ Code generation complete!")
    print("\nNext steps:")
    print("1. Review generated files in generated/ directory")
    print("2. Start Temporal worker: python temporal/worker.py")
    print("3. Execute workflow: python temporal/client_start_workflow.py")

if __name__ == "__main__":
    # Example usage
    instruction = """
    Create a workflow that:
    1. Fetches an order by ID
    2. Sends a confirmation email to the customer
    3. Saves the order status to database
    """
    
    generate_temporal_code(instruction)