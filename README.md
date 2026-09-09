# J-Bot 🤖

An extensible Python AI assistant built around tool calling. J-bot decides when it needs an external capability, calls a tool, and uses the result to answer.

## What's New in v3

- ✅ Modular package (`jbot/`) instead of one large script
- ✅ Native OpenAI-style tool calling (no regex parsing)
- ✅ Conversation history across turns
- ✅ Sandboxed file tools (cross-platform safe)
- ✅ Terminal TUI (green you / magenta J-BOT panels)
- ✅ Flexible LLM support (any OpenAI-compatible provider)
- ✅ Persistent memory with `/memorize` and `/recall`
- ✅ Lightweight (removed `torch` / `transformers`)

```text
USER → J-BOT AGENT → optional TOOL → TOOL RESULT → RESPONSE
```

## Quick Start

### Installation

```bash
pip install -r requirements.txt
python setup.py
```

`setup.py` guides you through:
- LLM provider configuration (local Ollama/LM Studio or custom/remote API)
- Optional SMTP credentials for email tools

### Run

```bash
python -m jbot
```

Opens an interactive full-screen TUI. Type your queries and watch the agent reason in real-time.

### Commands

- `/help` - Show all available commands
- `/tools` - List registered tools
- `/search <query>` - Web search
- `/clear` - Clear conversation history
- `/mem` - Show current memory
- `/memorize <key> <value>` - Store a fact permanently
- `/recall <key>` - Retrieve a stored fact
- `/save <name>` - Save current session
- `/load <name>` - Load a previous session
- `/sessions` - List saved sessions
- `/plan <goal>` - Create and execute a multi-step plan

**Keyboard Shortcuts:**
- `Ctrl+C` - Cancel current operation
- `Ctrl+Q` - Quit
- `Y/N` - Confirm/deny deletions

## Tools (30+)

### Data & Analysis
`calculate` • `read_spreadsheet` • `write_csv` • `calculate_roi` • `remember` • `recall` • `forget` • `list_memories`

### Web & API
`search` • `fetch_page` • `get_weather` • `get_news` • `get_github_info` • `wikipedia_search` • `get_stock_price`

### Communication
`send_email` • `send_notification` • `speak_text`

### System & Files
`system_info` • `read_file` • `write_file` • `remove_file` • `shell_run`

### Security
`vault_set` • `vault_get` • `vault_list` (requires `cryptography`)

### Language
`translate_text`

**Note:** All file operations stay inside `JBOT_SANDBOX` (project root by default).

## Configuration

After running `setup.py`, edit `.env`:

```env
# LLM Setup (Required)
USER_LLM_API_KEY=your-api-key
USER_LLM_BASE_URL=https://api.inceptionlabs.ai/v1
USER_LLM_MODEL=mercury-2

# Runtime Settings
JBOT_SANDBOX=.                    # Sandbox directory
JBOT_MAX_STEPS=8                  # Max tool calls per query
JBOT_TIMEOUT=60                   # Request timeout (seconds)
JBOT_TEMPERATURE=0.2              # LLM creativity (0.0-1.0)
JBOT_HISTORY_LIMIT=20             # Messages to retain per session

# Optional: Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
```

## Project Structure

```
jbot/                   agent runtime, LLM client, tools, terminal UI
agent.py                CLI entry (backward compatible)
lfm.py                  compatibility shim
tests/                  unit tests
setup.py                interactive setup wizard
requirements.txt        Python dependencies
```

## Extending J-Bot

### Add Custom Tools

Create a tool in `jbot/tools/`:

```python
from jbot.tools.registry import tool

@tool(name="my_tool")
def my_tool(param1: str, param2: int = 10) -> str:
    """
    Tool description for the LLM.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (optional)
    
    Returns:
        Result as a string
    """
    return f"Result: {param1} × {param2}"
```

The `@tool` decorator automatically registers it!

## Testing

```bash
python -m pytest tests -q
```

## Termux (Android) Notes

If you encounter issues installing `cryptography`:

1. Use system package manager: `pkg install python-cryptography`
2. Or install pre-compiled binaries: `pip install --only-binary :all: cryptography`
3. Without cryptography, vault features will be unavailable, but all other features work normally

## License

MIT License. See [LICENSE](LICENSE) for details.

## Support

- **Issues:** [Report bugs](https://github.com/novastardev/J-bot/issues)
- **Discussions:** [Ask questions](https://github.com/novastardev/J-bot/discussions)
- **Docs:** Check docstrings in `jbot/` code
- **Examples:** See tool implementations

---

Made with ❤️ by the J-Bot Community
