"""
FastAPI backend for Temporal workflow code generation.
Accepts frontend requests with prompts and generates Temporal code.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.workflow_orchestrator import code_generation_workflow

app = FastAPI(
    title="Temporal Code Generator API",
    description="Generate Temporal workflows from natural language prompts",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateCodeRequest(BaseModel):
    """Request model for code generation"""
    prompt: str

class GenerateCodeResponse(BaseModel):
    """
    Consistent response model for code generation with verification.
    All keys are always present with consistent names for frontend parsing.
    """
    # Always present - core response fields
    status: str  # "success", "failed", "warning" (based on verification)
    message: str  # Human readable message
    timestamp: str  # When the response was generated
    
    # Always present - data container
    data: Dict = {}  # Contains: prompt, generated_files, instruction, verification_status
    
    # Always present - error information (null if no error)
    error: Optional[str] = None  # Error message (null on success)
    error_code: Optional[str] = None  # Error code (null on success)
    error_details: Optional[Dict] = None  # Additional error details (null on success)
    
    # Verification information
    verification_status: Optional[str] = None  # "PASSED", "FAILED", or None
    verification_summary: Optional[Dict] = None  # Verification errors/warnings count

@app.post("/api/generate-workflow", response_model=GenerateCodeResponse)
async def generate_workflow(request: GenerateCodeRequest):
    """
    Generate a Temporal workflow from a natural language prompt.
    
    Request payload:
    {
        "prompt": "create a workflow named as payment and has 2 activity that are named as activity1 and activity2 with retry duration of 10 sec"
    }
    
    Always returns consistent response structure with all keys present.
    """
    timestamp = datetime.utcnow().isoformat()
    
    try:
        # Validate request
        if not request.prompt or not request.prompt.strip():
            print("❌ Invalid request: Empty prompt")
            return GenerateCodeResponse(
                status="failed",
                message="Prompt cannot be empty",
                timestamp=timestamp,
                data={
                    "prompt": request.prompt,
                    "generated_files": [],
                    "instruction": None,
                    "next_steps": []
                },
                error="Prompt cannot be empty",
                error_code="VALIDATION_ERROR",
                error_details={"field": "prompt", "reason": "empty_or_null"}
            )
        
        print(f"\n📨 Received API request with prompt: {request.prompt}")
        
        # Execute the workflow (Generator + Verifier)
        try:
            result = code_generation_workflow(request.prompt)
        except Exception as workflow_error:
            print(f"❌ Error in workflow execution: {workflow_error}")
            import traceback
            traceback.print_exc()
            return GenerateCodeResponse(
                status="failed",
                message="❌ Workflow execution failed: Unknown error",
                timestamp=timestamp,
                data={
                    "prompt": request.prompt,
                    "generated_files": [],
                    "instruction": None,
                    "verification_status": None
                },
                error="Workflow failed",
                error_code="WORKFLOW_FAILED",
                error_details={"reason": str(workflow_error)},
                verification_status=None,
                verification_summary=None
            )
        
        # Handle workflow result
        workflow_status = result.get("status", "unknown")
        workflow_data = result.get("data", {})
        workflow_error = result.get("error")
        workflow_error_details = result.get("error_details")
        
        # Extract generated files
        generated_files = []
        generated_file_dict = workflow_data.get("generated_files", {})
        if isinstance(generated_file_dict, dict):
            for filename, content in generated_file_dict.items():
                if content:  # Only add if content exists
                    generated_files.append(filename)
        
        if workflow_status == "success":
            print(f"✅ Workflow succeeded for prompt: {request.prompt[:50]}...")
            return GenerateCodeResponse(
                status="success",
                message="✅ Workflow generated and verified successfully",
                timestamp=timestamp,
                data=workflow_data,
                error=None,
                error_code=None,
                error_details=None,
                verification_status="PASSED",
                verification_summary=None
            )
        
        elif workflow_status == "warning":
            print(f"⚠️  Workflow completed with warnings for prompt: {request.prompt[:50]}...")
            return GenerateCodeResponse(
                status="warning",
                message="⚠️ Workflow generated but verification found issues",
                timestamp=timestamp,
                data=workflow_data,
                error=workflow_error,
                error_code="VERIFICATION_ISSUES",
                error_details=workflow_error_details,
                verification_status="FAILED",
                verification_summary=None
            )
        
        else:  # failed
            print(f"❌ Workflow failed for prompt: {request.prompt[:50]}...")
            return GenerateCodeResponse(
                status="failed",
                message=f"❌ Workflow execution failed: {result.get('message', 'Unknown error')}",
                timestamp=timestamp,
                data=workflow_data,
                error=workflow_error,
                error_code="WORKFLOW_FAILED",
                error_details=workflow_error_details,
                verification_status=None,
                verification_summary=None
            )
    
    except Exception as e:
        print(f"❌ Unexpected error in generate_workflow endpoint: {e}")
        import traceback
        traceback.print_exc()
        
        return GenerateCodeResponse(
            status="failed",
            message="An unexpected error occurred",
            timestamp=timestamp,
            data={
                "prompt": request.prompt if 'request' in locals() else None,
                "generated_files": [],
                "instruction": None,
                "next_steps": []
            },
            error=str(e),
            error_code="UNEXPECTED_ERROR",
            error_details={
                "exception_type": type(e).__name__,
                "endpoint": "generate_workflow"
            }
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "service": "Temporal Code Generator API"
        }
    except Exception as e:
        print(f"❌ Error in health check: {e}")
        return {
            "status": "unhealthy",
            "service": "Temporal Code Generator API",
            "error": str(e)
        }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Temporal Code Generator API",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "generate": "/api/generate-workflow"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
