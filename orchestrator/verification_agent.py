"""
Verification Agent - Simple LLM-based code verification (POC).
"""
import sys
from pathlib import Path
from typing import Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.llm_client import generate_code


def verify_workflow_code(activities_code: str, workflow_code: str) -> Dict:
    """
    Verify code using LLM with a dedicated verification prompt.
    
    Args:
        activities_code: Generated activities Python code
        workflow_code: Generated workflow Python code
        
    Returns:
        dict with verification results (standard format)
    """
    print("\n🔍 Verification Agent: Starting code verification...")
    
    # Call LLM with verification prompt
    verification_prompt = f"""
You are an expert in Temporal workflow code review. Analyze the following code for ANY ERRORS:
- Syntax errors
- Logic errors
- Missing error handling
- Resource leaks
- Incorrect Temporal patterns
- Type mismatches
- Race conditions
- Any other issues

Activities Code:
```python
{activities_code}
```

Workflow Code:
```python
{workflow_code}
```

Respond in JSON format:
{{
    "has_errors": true|false,
    "errors": ["error 1", "error 2", ...],
    "warnings": ["warning 1", "warning 2", ...],
    "is_valid": true|false,
    "summary": "Brief summary of verification result"
}}
"""
    
    try:
        print("  🤖 Calling LLM for verification...")
        response = generate_code(verification_prompt)
        
        # Parse JSON response
        import json
        response = response.replace("```json", "").replace("```", "").strip()
        result = json.loads(response)
        
        has_errors = result.get("has_errors", False)
        errors = result.get("errors", [])
        warnings = result.get("warnings", [])
        is_valid = result.get("is_valid", True)
        summary = result.get("summary", "Verification completed")
        
        # Log results
        print(f"  📊 Verification Status: {'PASSED ✅' if is_valid else 'FAILED ❌'}")
        
        if errors:
            print(f"  ❌ Errors found: {len(errors)}")
            for i, error in enumerate(errors, 1):
                print(f"     {i}. {error}")
        
        if warnings:
            print(f"  ⚠️  Warnings: {len(warnings)}")
            for i, warning in enumerate(warnings, 1):
                print(f"     {i}. {warning}")
        
        if not errors and not warnings:
            print("  ✅ No errors or warnings found")
        
        # Return with standard keys
        return {
            "status": "success" if is_valid else "failed",
            "message": "Code verified successfully" if is_valid else "Code verification found issues",
            "data": {
                "verification_status": "PASSED" if is_valid else "FAILED",
                "is_valid": is_valid,
                "has_errors": has_errors,
                "errors": errors,
                "warnings": warnings,
                "summary": summary
            },
            "error": None if is_valid else "Verification found issues",
            "error_details": None if is_valid else {"errors": errors, "warnings": warnings}
        }
    
    except Exception as e:
        print(f"  ❌ Verification failed: {e}")
        return {
            "status": "failed",
            "message": "Code verification failed",
            "data": {
                "verification_status": "FAILED",
                "is_valid": False,
                "has_errors": True,
                "errors": [f"Verification error: {str(e)}"],
                "warnings": [],
                "summary": f"Verification failed due to: {str(e)}"
            },
            "error": str(e),
            "error_details": {"errors": [f"Verification error: {str(e)}"]}
        }
