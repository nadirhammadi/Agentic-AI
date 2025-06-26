import sys
import os
import argparse
import logging
import json
from datetime import datetime
from dotenv import load_dotenv

from google import genai
from google.genai import types
from functions.generate_tests import generate_tests 
from call_function import call_function, available_functions
from config import MAX_ITERS
from prompts import system_prompt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def main():
    load_dotenv()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument("prompt", nargs="+", help="User prompt for the AI")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--model", default="gemini-2.0-flash-001", help="Gemini model to use")
    parser.add_argument("--dry-run", action="store_true", help="Prevent file modifications and execution")
    parser.add_argument("--testgen", action="store_true", help="Generate tests for a specific file")
    args = parser.parse_args()

    # Handle test generation mode
    if args.testgen:
        if len(args.prompt) < 1:
            logger.error("Usage: python main.py --testgen <file.py>")
            sys.exit(1)
        file_path = " ".join(args.prompt)
        result = generate_tests(file_path)
        print(result)
        sys.exit(0)

    # Validate API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    user_prompt = " ".join(args.prompt)

    # Configure verbose logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug(f"Using model: {args.model}")
        logger.debug(f"User prompt: {user_prompt}")
        if args.dry_run:
            logger.debug("DRY-RUN MODE: File modifications and execution disabled")

    # Initialize message history
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    conversation_history = []

    iters = 0
    final_response = None
    while True:
        iters += 1
        if iters > MAX_ITERS:
            logger.warning(f"Maximum iterations ({MAX_ITERS}) reached")
            break

        try:
            final_response, response = generate_content(
                client=client,
                messages=messages,
                model=args.model,
                verbose=args.verbose,
                dry_run=args.dry_run
            )
            
            # Add to conversation history
            conversation_history.append({
                "iteration": iters,
                "messages": [msg.to_dict() for msg in messages],
                "response": response.text if response else None
            })
            
            if final_response:
                logger.info("Final response:")
                print(final_response)
                break
                
        except Exception as e:
            logger.error(f"Error in generate_content: {str(e)}")
            conversation_history.append({
                "iteration": iters,
                "error": str(e),
                "messages": [msg.to_dict() for msg in messages]
            })
            break

    # Save conversation history
    try:
        history_file = "agent_history.json"
        with open(history_file, "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "user_prompt": user_prompt,
                "model": args.model,
                "iterations": iters,
                "dry_run": args.dry_run,
                "conversation": conversation_history
            }, indent=2) + "\n")
        logger.info(f"Conversation history saved to {history_file}")
    except Exception as e:
        logger.error(f"Failed to save history: {str(e)}")


def generate_content(client, messages, model, verbose, dry_run=False):
    try:
        # Generate content with retry mechanism
        response = client.models.generate_content(
            model=model,
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt
            ),
            retry=genai.types.RetryStrategy(max_retries=3)
        )

        # Monitor token usage
        if verbose and response.usage_metadata:
            logger.debug(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            logger.debug(f"Response tokens: {response.usage_metadata.candidates_token_count}")
            
            MAX_TOKENS = 8000
            if response.usage_metadata.prompt_token_count > MAX_TOKENS * 0.9:
                logger.warning("Prompt token count approaching model limit")

        # Process response candidates
        if response.candidates:
            for candidate in response.candidates:
                if candidate.content:
                    messages.append(candidate.content)

        # Check for final response
        if not response.function_calls:
            return response.text, response

        # Process function calls
        function_responses = []
        for function_call_part in response.function_calls:
            function_call_result = call_function(
                function_call_part=function_call_part,
                verbose=verbose,
                dry_run=dry_run
            )
            
            if (function_call_result.parts and 
                function_call_result.parts[0].function_response):
                function_responses.append(function_call_result.parts[0])
                
                if verbose:
                    func_name = function_call_part.name
                    logger.debug(f"Function response for {func_name}:")
                    logger.debug(function_call_result.parts[0].function_response.response)

        if not function_responses:
            raise Exception("No function responses generated")

        # Add tool responses to conversation
        messages.append(types.Content(role="tool", parts=function_responses))
        return None, response

    except genai.types.GenerationError as e:
        logger.error(f"API generation error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in content generation: {str(e)}")
        if verbose:
            import traceback
            logger.debug(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()