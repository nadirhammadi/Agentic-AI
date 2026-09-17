from google.genai import types

from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.run_python import run_python_file, schema_run_python_file
from functions.write_file_content import write_file, schema_write_file
from config import WORKING_DIR

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

FUNCTION_MAP = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

# Functions that mutate the filesystem or execute code; skipped in dry-run mode.
SIDE_EFFECT_FUNCTIONS = {"run_python_file", "write_file"}


def _function_response(function_name, response):
    return types.Content(
        role="user",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response=response,
            )
        ],
    )


def call_function(function_call_part, verbose=False, dry_run=False):
    function_name = function_call_part.name
    if verbose:
        print(f" - Calling function: {function_name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_name}")

    if function_name not in FUNCTION_MAP:
        return _function_response(
            function_name, {"error": f"Unknown function: {function_name}"}
        )

    if dry_run and function_name in SIDE_EFFECT_FUNCTIONS:
        return _function_response(
            function_name,
            {
                "result": f"[DRY RUN] Skipped '{function_name}' "
                f"(args={dict(function_call_part.args)}); no files were "
                f"modified and no code was executed."
            },
        )

    args = dict(function_call_part.args)
    args["working_directory"] = WORKING_DIR
    function_result = FUNCTION_MAP[function_name](**args)
    return _function_response(function_name, {"result": function_result})
