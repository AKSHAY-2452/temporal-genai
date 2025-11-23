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
        tuple of (activities_code, workflow_code) or ("", "") on failure
    """
    try:
        # Extract activities
        act_start = code.find("### ACTIVITIES_START ###")
        act_end = code.find("### ACTIVITIES_END ###")
        
        if act_start == -1 or act_end == -1:
            print("⚠️  Warning: Could not find ACTIVITIES markers in generated code")
            activities = ""
        else:
            activities = code[act_start + len("### ACTIVITIES_START ###"):act_end].strip()
        
        # Extract workflow
        wf_start = code.find("### WORKFLOW_START ###")
        wf_end = code.find("### WORKFLOW_END ###")
        
        if wf_start == -1 or wf_end == -1:
            print("⚠️  Warning: Could not find WORKFLOW markers in generated code")
            workflow = ""
        else:
            workflow = code[wf_start + len("### WORKFLOW_START ###"):wf_end].strip()
        
        # Clean up markdown code blocks if present
        activities = activities.replace("```python", "").replace("```", "").strip()
        workflow = workflow.replace("```python", "").replace("```", "").strip()
        
        return activities, workflow
    except Exception as e:
        print(f"❌ Error parsing generated code: {e}")
        return "", ""

def save_generated_files(activities_code: str, workflow_code: str) -> dict:
    """Save generated code to files.
    
    Returns:
        dict with save status and file paths
    """
    try:
        generated_dir = Path(__file__).parent.parent / "generated"
        generated_dir.mkdir(exist_ok=True)
        
        # Create __init__.py if it doesn't exist
        init_file = generated_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")
        
        saved_files = []
        
        # Save activities
        try:
            activities_file = generated_dir / "activities.py"
            activities_file.write_text(activities_code)
            print(f"✅ Generated: {activities_file}")
            saved_files.append(str(activities_file))
        except Exception as e:
            print(f"❌ Failed to save activities file: {e}")
        
        # Save workflow
        try:
            workflow_file = generated_dir / "workflow.py"
            workflow_file.write_text(workflow_code)
            print(f"✅ Generated: {workflow_file}")
            saved_files.append(str(workflow_file))
        except Exception as e:
            print(f"❌ Failed to save workflow file: {e}")
        
        return {
            "success": len(saved_files) > 0,
            "files_saved": saved_files,
            "message": f"Saved {len(saved_files)} files" if saved_files else "Failed to save any files"
        }
    except Exception as e:
        print(f"❌ Error saving generated files: {e}")
        return {
            "success": False,
            "files_saved": [],
            "message": f"Error saving files: {str(e)}"
        }

def _create_response(status: str, error: str = None, files_generated: list = None, 
                     instruction: str = None, message: str = None, details: dict = None) -> dict:
    """
    Helper to create consistent response structure across all scenarios.
    
    Args:
        status: "success", "failed"
        error: Error message (None if no error)
        files_generated: Dict of {filename: content}
        instruction: The instruction that was processed
        message: Additional message about the result
        details: Additional details about the error or process
        
    Returns:
        Consistently structured dict with 'data' key for new format
    """
    if files_generated is None:
        files_generated = {}
    
    return {
        "status": status,
        "message": message,
        "error": error,
        "data": {
            "instruction": instruction,
            "generated_files": files_generated,
            "details": details or {}
        }
    }


def generate_temporal_code(user_instruction: str) -> dict:
    """
    Main function to generate Temporal workflow and activities.
    Includes comprehensive error handling with try-except blocks.
    Returns consistent response structure for ALL scenarios.
    
    Args:
        user_instruction: Natural language description of what to build
        
    Returns:
        dict with CONSISTENT structure: status, instruction, files_generated, 
        message, error, details, next_steps (always same keys)
    """
    try:
        print("🤖 Starting code generation...")
        print(f"📝 Instruction: {user_instruction}")
        
        # Get available tools
        try:
            print("🔧 Fetching available MCP tools...")
            tools_description = get_tools_prompt()
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch MCP tools: {e}")
            tools_description = ""
        
        # Load and format prompt
        try:
            print("📄 Building prompt...")
            template = load_prompt_template()
            prompt = template.format(
                user_instruction=user_instruction,
                tools=tools_description
            )
        except Exception as e:
            print(f"❌ Error building prompt: {e}")
            return _create_response(
                status="failed",
                error=f"Failed to build prompt: {str(e)}",
                instruction=user_instruction,
                message="Prompt building failed",
                details={"stage": "prompt_building", "exception": str(e)}
            )
        
        # Generate code
        try:
            print("🧠 Calling LLM to generate code...")
            generated_code = generate_code(prompt)
        except Exception as e:
            print(f"❌ Error calling LLM: {e}")
            return _create_response(
                status="failed",
                error=f"Failed to generate code from LLM: {str(e)}",
                instruction=user_instruction,
                message="LLM code generation failed",
                details={"stage": "code_generation", "exception": str(e)}
            )
        
        # Parse generated code
        try:
            print("📦 Parsing generated code...")
            activities, workflow = parse_generated_code(generated_code)
            
            if not activities or not workflow:
                print("❌ Generated code appears to be empty - prompt may not be suitable for Temporal workflows")
                return _create_response(
                    status="failed",
                    error="Could not generate valid Temporal code from the prompt",
                    instruction=user_instruction,
                    message="The prompt does not seem to describe a distributed workflow task. Temporal workflows are for long-running, distributed business processes.",
                    details={
                        "stage": "code_parsing", 
                        "reason": "Generated code was empty. Hint: Use prompts like 'Create a workflow that processes payments with retry logic' instead of 'Download an app'."
                    }
                )
        except Exception as e:
            print(f"❌ Error parsing generated code: {e}")
            return _create_response(
                status="failed",
                error=f"Failed to parse generated code: {str(e)}",
                instruction=user_instruction,
                message="Code parsing failed",
                details={"stage": "code_parsing", "exception": str(e)}
            )
        
        # Save files
        try:
            print("💾 Saving files...")
            save_result = save_generated_files(activities, workflow)
        except Exception as e:
            print(f"❌ Error saving files: {e}")
            return _create_response(
                status="failed",
                error=f"Failed to save generated files: {str(e)}",
                instruction=user_instruction,
                message="File saving failed",
                details={"stage": "file_saving", "exception": str(e)}
            )
        
        print("\n✨ Code generation complete!")
        
        # Success
        if save_result["success"]:
            return _create_response(
                status="success",
                instruction=user_instruction,
                files_generated={
                    "activities.py": activities,
                    "workflow.py": workflow
                },
                message="Workflow generated successfully",
                details={"files_saved": save_result["files_saved"]}
            )
        else:
            return _create_response(
                status="failed",
                error=save_result["message"],
                instruction=user_instruction,
                files_generated={},
                message="Failed to save generated files",
                details={"stage": "file_saving", "reason": save_result["message"]}
            )
    
    except Exception as e:
        print(f"❌ Unexpected error in generate_temporal_code: {e}")
        import traceback
        traceback.print_exc()
        return _create_response(
            status="failed",
            error=f"Unexpected error: {str(e)}",
            instruction=user_instruction,
            message="An unexpected error occurred",
            details={"stage": "unknown", "error_type": type(e).__name__, "exception": str(e)}
        )

if __name__ == "__main__":
    # Example usage
    instruction = """
    Create a workflow that:
    1. Fetches an order by ID
    2. Sends a confirmation email to the customer
    3. Saves the order status to database
    """
    
    generate_temporal_code(instruction)