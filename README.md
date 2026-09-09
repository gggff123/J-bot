# J-Bot 🤖

**An extensible Python AI agent that thinks, plans, and gets things done.**

J-bot is a modular AI assistant framework built around intelligent tool calling. It decides when it needs external capabilities, calls the right tool, and uses results to deliver accurate answers. Perfect for automation, research, and interactive workflows.

---

## 🌟 Key Features

- **🔧 Native Tool Calling** – OpenAI-style function calling with 30+ built-in tools
- **💭 Multi-Step Reasoning** – Autonomous planning and execution of complex goals  
- **📝 Persistent Memory** – Remember facts and recall details across sessions with `/memorize` and `/recall`
- **💬 Conversation History** – Maintain context across multiple turns (configurable, default 20 messages)
- **🎨 Terminal UI** – Full-screen TUI with green/magenta panels and real-time streaming
- **🔓 Flexible LLM Support** – Works with any OpenAI-compatible API (Inception Labs, OpenAI, Groq, local Ollama/LM Studio)
- **🔒 Sandboxed Tools** – File operations stay within configured sandbox directory
- **⚡ Zero Lock-in** – Modular Python package; extend with custom tools easily

---

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- An LLM API key (optional – can use local Ollama/LM Studio)

### Installation

```bash
# Clone and install dependencies
git clone https://github.com/novastardev/J-bot.git
cd J-bot
pip install -r requirements.txt
```

### Configuration

Run the interactive setup wizard:

```bash
python setup.py
```

This will guide you through:
1. **LLM Provider** – Choose between:
   - Custom/Remote API (Inception Labs, OpenAI, Groq, etc.)
   - Existing local LLM (Ollama/LM Studio already running)
   - Auto-setup local model (installs Ollama and pulls a model)
2. **Optional SMTP** – For email sending capabilities

The wizard creates a `.env` file with your configuration.

### Running J-Bot

```bash
python -m jbot
```

Opens an interactive terminal interface. Type messages and watch the agent reason and use tools in real-time.

---

## 📋 Commands

Once inside J-Bot, use these commands:

| Command | Description |
|---------|-------------|
| `/help` | Show all available commands |
| `/tools` | List all registered tools |
| `/search <query>` | Web search |
| `/clear` | Clear conversation history |
| `/mem` | Show current memory |
| `/memorize <key> <value>` | Store a fact permanently |
| `/recall <key>` | Retrieve a stored fact |
| `/save <name>` | Save current session |
| `/load <name>` | Load a previous session |
| `/sessions` | List saved sessions |
| `/plan <goal>` | Create and execute a multi-step plan |

**Keyboard Shortcuts:**
- **Ctrl+C** – Cancel current operation
- **Ctrl+Q** – Quit J-Bot
- **y/n** – Confirm/deny file deletions

---

## 🛠️ Built-In Tools

J-Bot includes 30+ tools across these categories:

### 📊 Data & Analysis
- `calculate` – Math expressions
- `read_spreadsheet`, `write_csv` – File I/O
- `calculate_roi` – Financial calculations
- `remember`, `recall`, `forget`, `list_memories` – Persistent memory

### 🌐 Web & API
- `search` – Web search
- `fetch_page` – Fetch webpage content
- `get_weather` – Weather lookup
- `get_news` – Latest news
- `get_github_info` – GitHub repo/user details
- `wikipedia_search` – Wikipedia lookup
- `get_stock_price` – Stock market data

### 📧 Communication
- `send_email` – SMTP email (requires configuration)
- `send_notification` – System notifications
- `speak_text` – Text-to-speech

### 🖥️ System & Files
- `system_info` – OS/CPU/memory details
- `read_file`, `write_file`, `remove_file` – File operations (sandboxed)
- `shell_run` – Execute shell commands (sandboxed)

### 🔐 Security
- `vault_set`, `vault_get`, `vault_list` – Encrypted credential storage (requires `cryptography`)

### 🌍 Language & Translation
- `translate_text` – Multi-language translation

**Note:** All file operations are confined to `JBOT_SANDBOX` (project root by default).

---

## ⚙️ Configuration

Edit `.env` to customize behavior:

```env
# LLM Setup (required)
USER_LLM_API_KEY=your-api-key
USER_LLM_BASE_URL=https://api.inceptionlabs.ai/v1
USER_LLM_MODEL=mercury-2

# Runtime Limits
JBOT_SANDBOX=.                    # Sandbox directory for file ops
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

---

## 📦 Architecture

```
jbot/                   # Main package
  ├── agent.py         # Core reasoning loop
  ├── llm.py           # LLM client (OpenAI-compatible)
  ├── cli.py           # Terminal UI and commands
  ├── config.py        # Configuration loading
  ├── tools/           # Tool implementations
  │   ├── registry.py  # Tool registration
  │   ├── memory.py    # Persistent memory
  │   ├── web.py       # Web search & fetch
  │   ├── files.py     # File operations
  │   └── ...          # Other tools
  └── ui/              # Terminal UI components

agent.py                # Backward-compatible CLI entry
setup.py                # Interactive setup wizard
requirements.txt        # Python dependencies
tests/                  # Unit tests
```

---

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests -q
```

---

## 🔧 Extending J-Bot

### Adding Custom Tools

Create a tool in `jbot/tools/`:

```python
from jbot.tools.registry import tool

@tool(name="my_tool")
def my_tool(param1: str, param2: int = 10) -> str:
    """
    Tool description for the LLM.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Result as a string
    """
    return f"Result: {param1} * {param2}"
```

The `@tool` decorator automatically registers it with the agent.

---

## ⚠️ Platform-Specific Notes

### Termux (Android)

If `cryptography` installation fails:

```bash
# Option 1: Use system package manager
pkg install python-cryptography

# Option 2: Install pre-compiled binaries
pip install --only-binary :all: cryptography
```

**Note:** Without `cryptography`, vault features are unavailable, but all other tools work normally.

---

## 📊 What Changed in v3

- ✅ **Modular package** – `jbot/` module instead of monolithic script
- ✅ **Native OpenAI-style tool calling** – No regex parsing required
- ✅ **Conversation history** – Persistent context across turns
- ✅ **Sandboxed file tools** – Safe, cross-platform file operations
- ✅ **Terminal TUI** – Rich, interactive interface
- ✅ **Flexible LLM support** – Works with any OpenAI-compatible provider
- ✅ **Persistent memory** – `/memorize` and `/recall` commands
- ✅ **Lightweight** – Removed `torch`/`transformers` dependencies

---

## 🔄 How It Works

```
USER INPUT
    ↓
J-BOT AGENT (analyzes & reasons)
    ↓
NEEDS TOOL? 
    ├─ YES → EXECUTE TOOL → GET RESULT → LOOP BACK
    └─ NO → GENERATE RESPONSE
    ↓
FINAL ANSWER
```

The agent maintains conversation history, can recall facts from memory, and autonomously decides whether tools are needed.

---

## 📝 License

MIT License – See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Fork the repo, create a feature branch, and submit a pull request.

---

## 📞 Support

- **Issues:** Report bugs via GitHub Issues
- **Questions:** Check existing discussions or create a new one
- **Docs:** See `jbot/` docstrings and tool implementations for examples

---

## 🎯 Use Cases

- **Research Assistant** – Gather info, summarize findings, save to files
- **Automation** – Execute multi-step tasks, interact with APIs
- **Productivity** – Email, reminders, file management
- **Learning** – Explore concepts with tools and references
- **Custom Agents** – Extend with your own tools for specific workflows

---

**Made with ❤️ by the J-Bot community**
