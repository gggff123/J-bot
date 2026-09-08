import re
import inspect
import requests
import json
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

# ANSI color codes
C_RESET = "\033[0m"
C_RED = "\033[91m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_MAGENTA = "\033[95m"
C_CYAN = "\033[96m"
C_BOLD = "\033[1m"

# Mercury-2 API configuration
API_BASE = "https://api.inceptionlabs.ai/v1"
API_KEY = os.getenv("MERCURY_API_KEY", "sk_42d7fb03f8eb800748ea87862209e9d2")
MODEL = "mercury-2"

TOOLS = {}

def tool(func):
    TOOLS[func.__name__] = func
    return func

def get_tool_definitions():
    definitions = []
    for name, func in TOOLS.items():
        sig = inspect.signature(func)
        properties = {}
        required = []
        for param_name, param in sig.parameters.items():
            annotation = param.annotation
            if annotation == str:
                param_type = "string"
            elif annotation == int:
                param_type = "integer"
            elif annotation == float:
                param_type = "number"
            elif annotation == bool:
                param_type = "boolean"
            else:
                param_type = "string"
            properties[param_name] = {"type": param_type}
            if param.default is inspect.Parameter.empty:
                required.append(param_name)
        definitions.append({
            "type": "function",
            "function": {
                "name": name,
                "description": inspect.getdoc(func) or "",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }
        })
    return definitions

def generate(messages):
    """
    Send a chat completion request to the Mercury-2 API.
    Returns a string that may contain tool calls encoded in the custom format.
    """
    url = f"{API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": get_tool_definitions(),
        "tool_choice": "auto",
        "temperature": 0.0,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.exceptions.Timeout:
        return "Error: API request timed out. The service may be slow or unreachable."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the API. Please check your internet connection."

    if response.status_code != 200:
        error_msg = f"API error: {response.status_code} - {response.text[:200]}"
        print(error_msg)
        return f"Error: {error_msg}"

    data = response.json()
    choice = data["choices"][0]
    assistant_message = choice["message"]

    # Build the final string: text (if any) plus encoded tool calls
    output = ""
    if assistant_message.get("content"):
        output += assistant_message["content"]

    tool_calls = assistant_message.get("tool_calls", [])
    for tc in tool_calls:
        func_name = tc["function"]["name"]
        arguments = json.loads(tc["function"]["arguments"])
        # Build the argument string in the expected format: key='value'
        arg_parts = []
        for k, v in arguments.items():
            if isinstance(v, str):
                arg_parts.append(f"{k}='{v}'")
            else:
                arg_parts.append(f"{k}={v}")
        arg_str = ", ".join(arg_parts)
        output += f"<|tool_call_start|>{func_name}({arg_str})<|tool_call_end|>"

    return output

def parse_tool_calls(text):
    pattern = r"<\|tool_call_start\|>(.*?)<\|tool_call_end\|>"
    matches = re.findall(pattern, text, flags=re.DOTALL)
    calls = []
    for block in matches:
        block = block.strip()
        block = block.strip("[]").strip()
        match = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*)\)", block, flags=re.DOTALL)
        if not match:
            continue
        function_name = match.group(1)
        arguments_text = match.group(2).strip()
        arguments = {}
        if arguments_text:
            arg_pattern = re.compile(
                r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*'
                r'(?:"([^"]*)"|\'([^\']*)\'|([^,\s]+))'
            )
            for arg in arg_pattern.finditer(arguments_text):
                key = arg.group(1)
                value = arg.group(2) or arg.group(3) or arg.group(4)
                arguments[key] = value
        calls.append({"name": function_name, "arguments": arguments})
    return calls

def execute_tool(call):
    name = call["name"]
    arguments = call["arguments"]
    if name not in TOOLS:
        return f"Error: unknown tool '{name}'"
    try:
        return str(TOOLS[name](**arguments))
    except Exception as e:
        return f"Tool error: {e}"

def run_agent(user_input):
    messages = [
        {
            "role": "system",
            "content": (
                f"You are J-bot, an AI assistant originally created by gggff123 (the repo owner), with Novastar as a key collaborator. "
                f"You are running with model {MODEL} via API at {API_BASE}. "
                f"Your sandbox directory is {os.getcwd()}. "
                f"Current date/time: {datetime.datetime.now().isoformat()}. "
                "You have access to various tools. Use them when necessary. "
                "After receiving tool results, continue reasoning and provide the final answer."
            ),
        },
        {"role": "user", "content": user_input}
    ]

    while True:
        response = generate(messages)

        tool_calls = parse_tool_calls(response)
        if not tool_calls:
            return response

        # Build assistant message with tool_calls for API
        tool_calls_for_api = []
        for i, call in enumerate(tool_calls):
            tool_calls_for_api.append({
                "id": f"call_{i+1}",
                "type": "function",
                "function": {
                    "name": call["name"],
                    "arguments": json.dumps(call["arguments"])
                }
            })
        messages.append({
            "role": "assistant",
            "content": response,
            "tool_calls": tool_calls_for_api
        })

        for call in tool_calls:
            result = execute_tool(call)
            messages.append({
                "role": "tool",
                "name": call["name"],
                "content": result,
            })

def run_agent_loop(goal: str, max_steps: int = 5):
    planning_messages = [
        {
            "role": "system",
            "content": (
                "You are an autonomous planning agent. Break the goal into a "
                "numbered list of concrete, self-contained steps. Output ONLY "
                "the numbered list, one step per line."
            ),
        },
        {"role": "user", "content": goal},
    ]

    plan_text = generate(planning_messages)
    print("\nPLAN:")
    print(plan_text)

    steps = []
    for line in plan_text.splitlines():
        line = line.strip()
        match = re.match(r"^\s*(?:\d+[.)]\s*|[-*]\s+)(.+)$", line)
        if match:
            steps.append(match.group(1))

    if not steps:
        steps = [goal]
    steps = steps[:max_steps]

    context = ""
    last_result = ""
    for i, step in enumerate(steps, 1):
        print(f"\n=== STEP {i}/{len(steps)}: {step} ===")
        prompt = step
        if context:
            prompt = (
                "Results from previous steps:\n"
                f"{context}\n\n"
                f"Now complete this step: {step}"
            )
        last_result = run_agent(prompt)
        context += f"Step {i}: {last_result}\n"

    return last_result