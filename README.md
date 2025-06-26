# Agentic-AI
AI Code Assistant 

A local AI assistant using Google Gemini to help analyze, modify, and test your Python codebase.

Main Features

- Command-line interaction with a Gemini model to analyze and modify code
- Custom functions to list, read, write files, and execute Python code
- Automatic generation of unit tests with pytest via the special --testgen command
- Full conversation history saved as JSON
- Verbose mode to display detailed exchanges and function calls
- Robust error handling with logging
- --dry-run option to simulate without modifying files
- Support for configurable Gemini models

Installation

1. Clone this repository
   git clone <repository-url>
   cd <repo-name>

2. Create a Python virtual environment
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows

3. Install dependencies
   pip install -r requirements.txt

4. Create a .env file at the root and add your Gemini API key
   GEMINI_API_KEY=your_api_key_here

Usage

Run a simple query
   python main.py "Explain the main.py function"

Run with verbose mode for more details
   python main.py "Explain the main.py function" --verbose

Automatically generate tests for a Python file
   python main.py --testgen main.py

This command:
- generates a test file in tests/test_main.py
- runs the tests with pytest
- displays the test results in the console

Dry-run mode (simulation)
   python main.py "Modify config.py" --dry-run

The assistant simulates actions without modifying files or executing code.

Project Structure

.
├── call_function.py        # Management of functions called by Gemini
├── config.py               # Global configurations (e.g. MAX_ITERS, WORKING_DIR)
├── functions/              # Utility functions (read file, write, execute, generate tests)
│   ├── generate_tests.py   # Automatic unit test generation
│   ├── get_file_content.py
│   ├── get_files_info.py
│   ├── run_python.py
│   └── write_file_content.py
├── main.py                 # Main entry point and AI conversation loop
├── prompts.py              # System prompts used by Gemini
├── README.txt              # This file
├── requirements.txt        # Python dependencies
├── tests/                  # Automatically generated tests
└── .env                    # Environment variables (Gemini API key)

Customization

- Modify config.py to change Gemini model, working directory, max iterations, etc.
- Modify prompts.py to adjust the system prompt sent to Gemini.

Contributing

Contributions welcome!  
Please open an issue or a PR for any improvements.

License

Open-source MIT license project.
