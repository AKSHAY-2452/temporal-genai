"""
LLM Client for code generation using Groq (Free & Fast).
"""
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_code(prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
    """
    Generate code using Groq's LLM API.
    
    Args:
        prompt: The prompt containing instructions and context
        model: Groq model to use (default: llama-3.3-70b-versatile)
               Other options: mixtral-8x7b-32768, llama-3.1-70b-versatile
        
    Returns:
        Generated code as string
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Python developer specializing in Temporal workflows. Generate clean, production-ready code."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,  # Lower temperature for more consistent code
            max_tokens=8000,  # Groq has generous token limits
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error calling Groq API: {e}")
        print("Make sure GROQ_API_KEY is set in your environment")
        raise