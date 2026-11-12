import os
from dotenv import load_dotenv
from openai import OpenAI
import argparse
from prompts import system_prompt
from call_function import available_functions, call_function

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    raise Exception("OPENROUTER_API_KEY not found in .env file")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)



parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()
# Now we can access `args.user_prompt`

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": args.user_prompt},
]

for _ in range(20):
    # call the model, handle responses, etc.
    response = client.chat.completions.create(
        model="openrouter/free",
       messages=messages,
       tools=available_functions,
    )

    message = response.choices[0].message
    if message.content is not None:
        print(message.content)
    messages.append(message.model_dump(exclude_none=True))

    if message.tool_calls is None or len(message.tool_calls) == 0:
        break

    for tool_call in message.tool_calls:
        result = call_function(tool_call, verbose=args.verbose)

        if "content" not in result:
            raise Exception("Error: content not found in result")
        if args.verbose:
            print(f"-> {result['content']}")
        else:
            print(result["content"].split("\n")[-1])

        messages.append(result)



    if not response.usage:
        raise Exception("Usage not found in response")

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Response tokens: {response.usage.completion_tokens}")

    if response.usage.completion_tokens == 0:
        break

if messages[-1]["role"] == "user":
    print("Error: No response from model")

