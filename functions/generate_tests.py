import os
import logging
import subprocess
from datetime import datetime
from google import genai
from google.genai import types
from config import WORKING_DIR
from utils.path_validation import validate_path

logger = logging.getLogger(__name__)

def generate_tests(file_path: str, 
                   working_directory: str = WORKING_DIR,
                   model: str = "gemini-1.5-flash-latest",
                   timeout: int = 60) -> str:
    """
    Generates unit tests for a Python file and runs them
    
    Args:
        file_path: Relative path to the Python file
        working_directory: Base directory for operations
        model: Gemini model to use for test generation
        timeout: Maximum execution time for tests (seconds)
    
    Returns:
        String with test generation and execution results
    """
    try:
        # Validate paths
        validated_path = validate_path(file_path, working_directory)
        test_dir = validate_path("tests", working_directory)
        
        # Verify file exists
        if not os.path.isfile(validated_path):
            return f"Error: File not found: {validated_path}"
        
        # Read file content
        with open(validated_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        
        # Initialize Gemini client
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "Error: GEMINI_API_KEY environment variable not set"
        
        client = genai.Client(api_key=api_key)
        
        # Create prompt with structured instructions
        module_name = file_path.replace('.py','').replace('/','.')
        prompt = (
            "Generate comprehensive pytest unit tests for the following Python code:\n\n"
            f"File: {file_path}\n"
            f"Current Date: {datetime.now().date()}\n\n"
            "```python\n"
            f"{file_content}\n"
            "```\n\n"
            "## Instructions:\n"
            "1. Focus on testing core functionality and edge cases\n"
            "2. Cover all significant functions and classes\n"
            "3. Include docstrings explaining each test case\n"
            "4. Use mocks for external dependencies\n"
            "5. Follow this template:\n\n"
            "```python\n"
            "import pytest\n"
            f"from {module_name} import *\n\n"
            "def test_main_functionality():\n"
            "    \"\"\"Test core functionality\"\"\"\n"
            "    # Test implementation\n\n"
            "def test_edge_cases():\n"
            "    \"\"\"Test boundary conditions\"\"\"\n"
            "    # Test implementation\n"
            "```"
        )
        
        # Generate tests with retry mechanism
        response = client.models.generate_content(
         model=model,
         contents=[types.Content(role="user", parts=[types.Part(text=prompt)])]
)

        
        if not response.text:
            return "Error: Failed to generate test code"
        
        test_code = response.text
        
        # Ensure tests directory exists
        os.makedirs(test_dir, exist_ok=True)
        
        # Create test file name
        base_name = os.path.basename(file_path)
        test_file = f"test_{base_name}"
        test_path = os.path.join(test_dir, test_file)
        
        # Validate test path
        validated_test_path = validate_path(test_path, working_directory)
        
        if test_code.startswith("```python"):
         test_code = test_code.strip("`").replace("python", "", 1).strip()
        if test_code.endswith("```"):
         test_code = test_code.rsplit("```", 1)[0].strip()
        
        # Write test file
        with open(validated_test_path, "w", encoding="utf-8") as f:
            f.write(test_code)
        
        # Run tests with timeout
        result = run_tests(validated_test_path, timeout)
        
        # Format results
        return (f"✅ Generated tests for {file_path}\n"
                f"📁 Test file: {validated_test_path}\n\n"
                f"🧪 Test results:\n{result}")
    
    except Exception as e:
        logger.error(f"Test generation failed: {str(e)}")
        return f"Error: {str(e)}"

def run_tests(test_path: str, timeout: int = 60) -> str:
    """Execute pytest with timeout handling"""
    try:
        result = subprocess.run(
            ["pytest", test_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return "⏰ Error: Test execution timed out"
    except FileNotFoundError:
        return "❌ Error: pytest not installed. Install with: pip install pytest"