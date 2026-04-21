import os, argparse, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from call_function import available_functions, call_function
from config import MAX_ITERATIONS

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")
    client = genai.Client(api_key=api_key)
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    
    for i in range(MAX_ITERATIONS):
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt,
                # temperature=0
                )
        )
        if not response.usage_metadata:
            raise RuntimeError("Gemini API response appears to be malformed")
        
        if response.candidates:
            for candidate in response.candidates:
                messages.append(candidate)

        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"""
            Prompt tokens: {response.usage_metadata.prompt_token_count}
            Response tokens: {response.usage_metadata.candidates_token_count}
            """)

        if response.function_calls:
            if i >= MAX_ITERATIONS:
                print("Error: Maximum iterations reached with no final response produced")
                sys.exit(1)
            function_results = []
            for function_call in response.function_calls:
                function_call_result = call_function(function_call, args.verbose)
                if not function_call_result.parts:
                    raise Exception("Error: calling function")
                if not function_call_result.parts[0].function_response:
                    raise Exception("Error: Function response is None")
                if not function_call_result.parts[0].function_response.response:
                    raise Exception("Error: No function response")
                
                function_results.append(function_call_result.parts[0])
                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")
            messages.append(types.Content(role="user", parts=function_results))
        else:
            print("Response:")
            print(response.text)
            break


if __name__ == "__main__":
    main()
