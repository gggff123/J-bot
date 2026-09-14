try:
    import re
    import inspect
    import ast
    import threading
    import warnings
    from llama_cpp import Llama
    from rich.console import Console
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.text import Text
    # Ignore the specific huggingface_hub deprecation warning
    warnings.filterwarnings("ignore", category=UserWarning, message=".*local_dir_use_symlinks.*")
    # ============================================================
    # CONSOLE
    # ============================================================

    console = Console()


    # ============================================================
    # MODEL
    # ============================================================

    REPO_ID = "LiquidAI/LFM2.5-1.2B-Instruct-GGUF"
    FILENAME = "*Q4_K_M.gguf"

    llm = Llama.from_pretrained(
        repo_id=REPO_ID,
        filename=FILENAME,
        n_ctx=4096,
        n_threads=None,
        n_gpu_layers=0,
        flash_attn=True,
        verbose=False,
    )


    # ============================================================
    # TOOLS
    # ============================================================

    TOOLS = {}


    def tool(func):
        TOOLS[func.__name__] = func
        return func


    def get_tool_definitions():

        definitions = []

        for name, func in TOOLS.items():

            signature = inspect.signature(func)

            properties = {}
            required = []

            for param_name, param in signature.parameters.items():

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
                    "description": func.__doc__ or "",
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            })

        return definitions


    # ============================================================
    # GENERATE STREAM
    # ============================================================

    def generate_stream(messages, on_token=None):

        stream = llm.create_chat_completion(
            messages=messages,
            tools=get_tool_definitions(),
            max_tokens=1080,
            temperature=0.0,
            stream=True,
        )

        statuses = [
            "Generating...",
            "Tinkering...",
            "Thinking...",
            "Working...",
            "Figuring things out...",
        ]

        stop_status = threading.Event()
        live = None
        status_thread = None

        full_text = ""
        first_token = True

        # --------------------------------------------------------
        # Status animation thread
        # --------------------------------------------------------

        def update_status():

            index = 0

            while not stop_status.is_set():

                live.update(
                    Spinner(
                        "dots",
                        text=Text(
                            statuses[index]
                        )
                    )
                )

                index = (index + 1) % len(statuses)

                # Change text every 5 seconds
                # but stop immediately when generation finishes.
                if stop_status.wait(5):
                    break

        # --------------------------------------------------------
        # Start Rich Live
        # --------------------------------------------------------

        live = Live(
            refresh_per_second=10,
            console=console,
        )

        live.start()

        status_thread = threading.Thread(
            target=update_status,
            daemon=True,
        )

        status_thread.start()

        try:

            for chunk in stream:

                choices = chunk.get("choices", [])

                if not choices:
                    continue

                delta = choices[0].get(
                    "delta",
                    {}
                )

                piece = delta.get("content")

                if not piece:
                    continue

                # ------------------------------------------------
                # First token arrived
                # ------------------------------------------------

                if first_token:

                    first_token = False

                    # Stop status animation
                    stop_status.set()

                    if status_thread:
                        status_thread.join(
                            timeout=1
                        )

                    # Remove Live display
                    live.update("")
                    live.stop()
                    live = None

                    console.print(
                        "\n[bold green]MODEL:[/]"
                    )

                # ------------------------------------------------
                # Save token
                # ------------------------------------------------

                full_text += piece

                # ------------------------------------------------
                # Send token to caller
                # ------------------------------------------------

                if on_token:
                    on_token(piece)

        finally:

            stop_status.set()

            if status_thread:
                status_thread.join(
                    timeout=1
                )

            if live is not None:
                live.update("")
                live.stop()

        return full_text


    # ============================================================
    # TOOL CALL PARSER
    # ============================================================

    def parse_tool_calls(text):

        calls = []

        # --------------------------------------------------------
        # Tagged format
        #
        # <|tool_call_start|>
        # hello(name="Hi")
        # <|tool_call_end|>
        # --------------------------------------------------------

        tagged_pattern = re.compile(
            r"<\|tool_call_start\|>\s*(.*?)\s*<\|tool_call_end\|>",
            re.DOTALL,
        )

        tagged_matches = tagged_pattern.findall(text)

        if tagged_matches:

            for match in tagged_matches:

                match = match.strip()

                function_match = re.match(
                    r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*)\)",
                    match,
                    re.DOTALL,
                )

                if not function_match:
                    continue

                name = function_match.group(1)

                arguments = function_match.group(2).strip()

                calls.append({
                    "name": name,
                    "arguments": arguments,
                })

            return calls

        # --------------------------------------------------------
        # Bare bracket format
        #
        # [hello(name="Hi")]
        #
        # IMPORTANT:
        # We only parse the bracketed form here.
        # We DON'T separately search for hello(...)
        # because that caused duplicate calls.
        # --------------------------------------------------------

        bare_pattern = re.compile(
            r"\[\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)\s*\]",
            re.DOTALL,
        )

        bare_matches = bare_pattern.findall(text)

        for name, arguments in bare_matches:

            calls.append({
                "name": name,
                "arguments": arguments.strip(),
            })

        return calls


    # ============================================================
    # EXECUTE TOOL
    # ============================================================

    def execute_tool(name, arguments):

        if name not in TOOLS:

            return (
                f"Tool '{name}' does not exist."
            )

        func = TOOLS[name]

        try:

            arguments = arguments.strip()

            # ----------------------------------------------------
            # No arguments
            # ----------------------------------------------------

            if not arguments:

                result = func()

                return str(result)

            # ----------------------------------------------------
            # Turn:
            #
            # name="Hi there!"
            #
            # into a real Python call:
            #
            # func(name="Hi there!")
            # ----------------------------------------------------

            expression = ast.parse(
                f"func({arguments})",
                mode="eval",
            )

            call = expression.body

            positional_args = []
            keyword_args = {}

            # ----------------------------------------------------
            # Positional arguments
            # ----------------------------------------------------

            for arg in call.args:

                positional_args.append(
                    ast.literal_eval(arg)
                )

            # ----------------------------------------------------
            # Keyword arguments
            # ----------------------------------------------------

            for keyword in call.keywords:

                if keyword.arg is None:

                    return (
                        "Tool error: **kwargs style "
                        "arguments are not supported."
                    )

                keyword_args[
                    keyword.arg
                ] = ast.literal_eval(
                    keyword.value
                )

            # ----------------------------------------------------
            # Execute
            # ----------------------------------------------------

            result = func(
                *positional_args,
                **keyword_args,
            )

            return str(result)

        except Exception as e:

            return (
                f"Tool execution error: "
                f"{type(e).__name__}: {e}"
            )


    # ============================================================
    # AGENT
    # ============================================================

    def run_agent(
        user_input,
        on_token=None,
    ):

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant. "
                    "Use tools when necessary."
                ),
            },
            {
                "role": "user",
                "content": user_input,
            },
        ]

        while True:

            # ----------------------------------------------------
            # Generate
            # ----------------------------------------------------

            response_text = generate_stream(
                messages,
                on_token=on_token,
            )

            # ----------------------------------------------------
            # Check tool calls
            # ----------------------------------------------------

            tool_calls = parse_tool_calls(
                response_text
            )

            # ----------------------------------------------------
            # Normal response
            # ----------------------------------------------------

            if not tool_calls:

                console.print()

                return response_text

            # ----------------------------------------------------
            # Save assistant message
            # ----------------------------------------------------

            messages.append({
                "role": "assistant",
                "content": response_text,
            })

            # ----------------------------------------------------
            # Execute tools
            # ----------------------------------------------------

            for call in tool_calls:

                name = call["name"]

                arguments = call["arguments"]

                console.print(
                    f"\n[bold yellow]CALLING[/] "
                    f"[cyan]{name}[/]"
                )

                console.print(
                    f"[dim]{arguments}[/]"
                )

                result = execute_tool(
                    name,
                    arguments,
                )

                console.print(
                    "[bold blue]TOOL RESULT:[/]"
                )

                console.print(
                    result
                )

                # ------------------------------------------------
                # Add result back to model
                # ------------------------------------------------

                messages.append({
                    "role": "tool",
                    "content": result,
                })
except ValueError:
    print("\nContext Limit reached.")
