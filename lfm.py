import re
import inspect

from llama_cpp import Llama


# --- Model config ---
REPO_ID = "LiquidAI/LFM2.5-1.2B-Instruct-GGUF"
# Pick a quant: Q4_K_M (~731MB, fastest/smallest), Q5_K_M, Q6_K, Q8_0 (best quality)
FILENAME = "*Q4_K_M.gguf"

# --- Automatic download + cache ---
# First run downloads via huggingface_hub and caches to ~/.cache/huggingface.
# Every subsequent run loads instantly from disk (mmap'd, no re-download).
llm = Llama.from_pretrained(
    repo_id=REPO_ID,
    filename=FILENAME,
    n_ctx=4096,
    n_threads=None,       # None = auto-detect all cores
    n_gpu_layers=0,       # bump this up if you have a GPU build of llama-cpp-python
    flash_attn=True,      # required for LFM2's hybrid attention/conv layers
    verbose=False,
)

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


def generate_stream(messages, on_token=None):
    """
    Streams tokens via llama.cpp's native streaming and returns the full
    decoded assistant text at the end. `tools` are passed so the model's
    own chat template (embedded in the GGUF) renders them into the prompt.
    """
    stream = llm.create_chat_completion(
        messages=messages,
        tools=get_tool_definitions(),
        max_tokens=1080,
        temperature=0.0,   # deterministic, matches do_sample=False
        stream=True,
    )

    full_text = ""

    for chunk in stream:
        delta = chunk["choices"][0]["delta"]
        piece = delta.get("content")

        if piece:
            full_text += piece
            if on_token:
                on_token(piece)

    return full_text


def parse_tool_calls(text):
    calls = []

    # Format 1: <|tool_call_start|>...<|tool_call_end|>
    tagged_pattern = r"<\|tool_call_start\|>(.*?)<\|tool_call_end\|>"
    tagged_matches = re.findall(tagged_pattern, text, flags=re.DOTALL)

    # Format 2: bare [func(args)] blocks (llama.cpp's rendering for this model)
    bare_pattern = r"\[([a-zA-Z_][a-zA-Z0-9_]*\([^\]]*\))\]"
    bare_matches = re.findall(bare_pattern, text, flags=re.DOTALL)

    blocks = tagged_matches + bare_matches

    for block in blocks:
        block = block.strip()
        block = block.strip("[]").strip()

        match = re.match(
            r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*)\)",
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


def run_agent(user_input, on_token=None):
    """
    on_token: optional callback(str) invoked per streamed chunk,
    e.g. `lambda t: print(t, end="", flush=True)`.
    """
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
        print("\nMODEL:")
        response = generate_stream(messages, on_token=on_token)
        print()

        tool_calls = parse_tool_calls(response)

        if not tool_calls:
            return response

        messages.append({
            "role": "assistant",
            "content": response,
        })

        for call in tool_calls:
            print(f"\nCALLING: {call['name']}({call['arguments']})")
            result = execute_tool(call)
            messages.append({
                "role": "tool",
                "name": call["name"],
                "content": result,
            })
