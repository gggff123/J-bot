import re
import inspect
import torch

from transformers import AutoTokenizer, AutoModelForCausalLM


MODEL_NAME = "LiquidAI/LFM2.5-1.2B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32,
    device_map="cpu",
)

model.eval()

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

            properties[param_name] = {
                "type": param_type
            }

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
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        tools=get_tool_definitions(),
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    )

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=False,
        )

    generated_tokens = output[0][inputs["input_ids"].shape[1]:]

    return tokenizer.decode(
        generated_tokens,
        skip_special_tokens=False
    )


def parse_tool_calls(text):
    pattern = (
        r"<\|tool_call_start\|>"
        r"(.*?)"
        r"<\|tool_call_end\|>"
    )

    matches = re.findall(
        pattern,
        text,
        flags=re.DOTALL
    )

    calls = []

    for block in matches:
        block = block.strip()
        block = block.strip("[]").strip()

        match = re.match(
            r"([a-zA-Z_][a-zA-Z0-9_]*)\s*"
            r"\((.*)\)",
            block,
            flags=re.DOTALL
        )

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

                value = (
                    arg.group(2)
                    if arg.group(2) is not None
                    else arg.group(3)
                    if arg.group(3) is not None
                    else arg.group(4)
                )

                arguments[key] = value

        calls.append({
            "name": function_name,
            "arguments": arguments,
        })

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
                "You are a helpful AI agent. "
                "Use tools when necessary. "
                "After receiving tool results, continue reasoning "
                "and provide the final answer."
            ),
        },
        {
            "role": "user",
            "content": user_input,
        }
    ]

    while True:
        response = generate(messages)

        print("\nMODEL:")
        print(response)

        tool_calls = parse_tool_calls(response)

        if not tool_calls:
            return response

        messages.append({
            "role": "assistant",
            "content": response,
        })

        for call in tool_calls:
            print(
                f"\nCALLING: {call['name']}"
                f"({call['arguments']})"
            )

            result = execute_tool(call)

            print("RESULT:", result)

            messages.append({
                "role": "tool",
                "name": call["name"],
                "content": result,
            })
