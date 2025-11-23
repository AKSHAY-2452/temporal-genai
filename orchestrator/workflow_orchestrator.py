"""
Workflow Orchestrator - Generates and verifies code (POC - simple, no correction).
"""
import sys
from pathlib import Path
from typing import Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.generator import generate_temporal_code
from orchestrator.verification_agent import verify_workflow_code


def code_generation_workflow(user_prompt: str) -> Dict:
    """
    Simple workflow - Generate code, verify it, return standard response (POC).
    
    Args:
        user_prompt: User's natural language prompt
        
    Returns:
        Dict with standard response keys
    """
    
    print("\n" + "="*60)
    print("🚀 WORKFLOW: Starting code generation & verification")
    print("="*60)
    
    # STEP 1: Generate code
    print("\n📝 STEP 1: Code Generation")
    print("-" * 40)
    
    generation_result = generate_temporal_code(user_prompt)
    
    if generation_result["status"] == "failed":
        print("❌ Generation failed")
        return generation_result
    
    # Extract generated code
    activities_code = generation_result.get("data", {}).get("generated_files", {}).get("activities.py", "")
    workflow_code = generation_result.get("data", {}).get("generated_files", {}).get("workflow.py", "")
    
    if not activities_code or not workflow_code:
        print("❌ No code generated")
        return {
            "status": "failed",
            "message": "Code generation produced empty files",
            "data": {},
            "error": "Empty files",
            "error_details": None
        }
    
    # STEP 2: Verify code
    print("\n✅ STEP 2: Code Verification")
    print("-" * 40)
    
    verification_result = verify_workflow_code(activities_code, workflow_code)
    
    is_valid = verification_result.get("data", {}).get("is_valid", False)
    
    # Combine results with standard keys
    final_result = {
        "status": "success" if is_valid else "warning",
        "message": "Code generated and verified" if is_valid else "Code generated with issues",
        "data": {
            "prompt": user_prompt,
            "generated_files": {
                "activities.py": activities_code,
                "workflow.py": workflow_code
            },
            "verification_status": verification_result.get("data", {}).get("verification_status"),
            "errors": verification_result.get("data", {}).get("errors", []),
            "warnings": verification_result.get("data", {}).get("warnings", [])
        },
        "error": None if is_valid else "Code has issues",
        "error_details": None if is_valid else {
            "errors": verification_result.get("data", {}).get("errors", [])
        }
    }
    
    print("\n" + "="*60)
    print(f"✅ WORKFLOW COMPLETE: {final_result['status']}")
    print("="*60 + "\n")
    
    return final_result


if __name__ == "__main__":
    pass

