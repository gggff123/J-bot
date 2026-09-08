# J-bot

An extensible Python AI assistant built around tool calling. J-bot decides when it needs an external capability, calls a tool, and uses the result to answer.

## What changed in v3

- Modular package (`jbot/`) instead of one large script
- Native OpenAI-style tool calling (no regex parsing of tool calls)
- Conversation history across turns
- Sandboxed file tools (no Windows-only `os.startfile`, no interactive `input()` inside tools)
- Terminal TUI (Nova X-style green you / magenta J-BOT panels)
- Unused `torch` / `transformers` removed; configure any OpenAI-compatible LLM
- Persistent memory: remember facts across conversations with `/memorize` and `/recall`

```text
USER -> J-BOT AGENT -> optional TOOL -> TOOL RESULT -> RESPONSE
```

## Setup

```bash
pip install -r requirements.txt
python setup.py
```

`setup.py` will guide you through configuring your LLM provider (local Ollama/LM Studio or custom/remote API) and optional tool credentials.

## Run

```bash
python -m jbot
```

Opens a full-screen TUI. Commands: `/help`, `/tools`, `/search <query>`, `/clear`, `/mem`, `/memorize <key> <value>`, `/recall <key>`, `/save <name>`, `/load <name>`, `/sessions`, `/plan <goal>`, `/exit`.

Ctrl+C cancels the current run. Ctrl+Q quits. Replies stream. Deletes ask `y`/`n` first.

## Tools

calculate, system_info, remember / recall / forget / list_memories, read_spreadsheet / write_csv / calculate_roi / send_email / send_notification / speak_text, create_file / read_file / list_files / move_file / copy_file / remove_file, get_weather, web_search, web_fetch, run_shell, github_user / github_users_repos / github_search / github_followers, get_news, translate_text, get_stock_price, wikipedia_summary.

File tools stay inside `JBOT_SANDBOX` (project root by default).

## Layout

```text
jbot/           agent runtime, LLM client, tools, terminal UI
agent.py        CLI entry (compat)
lfm.py          compat shim
tests/          unit tests
```

## Tests

```bash
python -m pytest tests -q
```

MIT License.
