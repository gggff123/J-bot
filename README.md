 <div align="center">

# 🤖 J-Bot

### Your AI assistant. Your tools. Your workflow.

**J-Bot is an experimental Python AI agent that connects language models to real tools — from web search and weather to file operations and GitHub.**

Move beyond a chatbot that only answers questions. Build an assistant that can retrieve information, interact with tools, inspect results, and help you get things done.

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Development Status](https://img.shields.io/badge/Status-Experimental-orange?style=flat-square)](https://github.com/gggff123/J-bot)
[![GitHub Stars](https://img.shields.io/github/stars/gggff123/J-bot?style=flat-square&logo=github)](https://github.com/gggff123/J-bot/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/gggff123/J-bot?style=flat-square)](https://github.com/gggff123/J-bot/issues)

[**Get Started**](#-getting-started) · [Features](#-features) · [Architecture](#-how-it-works) · [Contributing](#-contributing)

</div>

---

## 💡 What is J-Bot?

Most basic chatbots follow a simple pattern:

`User → AI model → Response`

J-Bot is built around a more capable approach:

`User → Agent → Tool → Result → Agent → Response`

When a task requires an external capability, the agent can use an available tool and incorporate the result into its response.

The goal is to create a flexible, extensible assistant where tools expand what a language model can do.

### ✨ What makes it interesting?

- **Tool-driven workflows:** Give an AI agent access to useful external capabilities.
- **Python-based:** Explore, modify, and extend the implementation.
- **Online and offline modes:** Choose a supported execution path through the setup wizard.
- **GitHub integration:** Bring repository-related capabilities into the assistant.
- **An evolving project:** Experiment with agent architecture, model integration, and practical automation.

## 🚀 Features

| Capability | What it does |
|---|---|
| 🧠 AI agent | Coordinates requests, tools, and results |
| 🔎 Web search | Retrieves information from the web |
| 🌦️ Weather | Accesses weather information |
| 🐙 GitHub integration | Provides GitHub-related tools and account actions |
| 📁 File operations | Works with files through available tools |
| 💻 System information | Retrieves information about the local system |
| 🧠 Memory | Supports assistant memory capabilities |
| 📡 Model integration | Supports online AI and local-model workflows |
| 🎨 Terminal interface | Uses Rich for terminal presentation |
| 🧩 Extensible design | Provides a foundation for adding more tools |

> **Note:** Available functionality can depend on the selected mode, model configuration, API credentials, and the current state of development.

## 🖥️ See it in action

A simple example is asking J-Bot to research a topic.

**You ask:**

```text
Search the web for information about Egypt.
Summarize the most useful findings.
```

**The intended workflow:**

```text
       YOUR REQUEST
            │
            ▼
       ┌─────────┐
       │ J-BOT   │
       │  AGENT  │
       └────┬────┘
            │
            ▼
      Select a tool
            │
            ▼
       Web Search
            │
            ▼
      Search Results
            │
            ▼
       J-Bot processes
        the results
            │
            ▼
      Final response
```

The agent's job is to connect your request with the available tools and use the returned information to formulate an answer.

> **Want to see the real experience?** Run J-Bot locally and capture a short terminal GIF here. A genuine demonstration of a tool call, its result, and the final response is the best way to show prospective users what the project actually does.

## ⚙️ How it works

J-Bot is organized around a few central responsibilities:

- **Agent:** Coordinates the user's request and the tool-use workflow.
- **Tools:** Provide capabilities such as search, weather, file operations, and GitHub integration.
- **Model:** Supplies the language-model capabilities used by the selected execution mode.
- **Interface:** Provides the terminal interaction.

Conceptually:

```text
J-Bot
├── Agent
│   ├── Understand the request
│   ├── Select available capabilities
│   ├── Process tool results
│   └── Produce a response
│
├── Tools
│   ├── Web Search
│   ├── Weather
│   ├── File Operations
│   ├── System Information
│   └── GitHub
│
├── Model Integration
│   ├── Offline mode
│   └── Online mode
│
└── Terminal Interface
```

This is a conceptual overview, not a guarantee that every capability is implemented as a separate module.

## 🛠️ Getting started

J-Bot currently provides a Windows batch setup wizard that installs dependencies and launches the selected mode.

### Requirements

- Windows with Command Prompt
- Python 3.x
- Git
- An internet connection for cloning the repository and installing dependencies
- An API key for online mode
- A compatible local-model setup for offline mode

### 1. Clone the repository

Open Command Prompt and run:

```cmd
git clone https://github.com/gggff123/J-bot.git
cd J-bot
```

### 2. Run the setup wizard

```cmd
setup.bat
```

The wizard will:

1. Check for and install `uv` if necessary.
2. Let you choose a virtual environment or system Python.
3. Install the project's Python dependencies.
4. Let you select offline or online mode.
5. Launch the corresponding entry point.

### 3. Choose your mode

**Offline mode**

The wizard launches `agent.py`. Make sure the required local model and configuration are available before using this mode.

**Online mode**

The wizard launches `ongent.py`. Configure the required API credentials and provider settings before using this mode.

The setup wizard installs dependencies, but it does not guarantee that every model, API provider, or credential is configured automatically.

For troubleshooting, check the terminal output and the project's current configuration before opening an issue.

## 🔐 Security and permissions

J-Bot can interact with tools that access files, system information, or GitHub.

- Review tool behavior before using it with sensitive files or repositories.
- Protect API keys and never commit secrets to the repository.
- Use a test repository when experimenting with GitHub write operations.
- Understand what a tool can change before granting it access to your account.

An AI-generated action should not be treated as automatically safe or correct.

## 🧪 Development status

J-Bot is **experimental and actively evolving**.

The APIs, architecture, model configuration, and tool behavior may change. Some workflows may require additional configuration, and bugs are possible.

This project is intended for experimentation, learning, and development — not as a guarantee of production-ready autonomous operation.

## 🗺️ Roadmap

Potential areas of continued development include:

- [ ] More reliable tool selection and execution
- [ ] Clearer configuration and first-run diagnostics
- [ ] Better error handling and recovery
- [ ] Improved documentation and real usage demonstrations
- [ ] Automated tests for important workflows
- [ ] More extensible tool registration
- [ ] Safer controls around actions that modify external systems

Have an idea that would make J-Bot more useful? [Open an issue](https://github.com/gggff123/J-bot/issues).

## 🤝 Contributing

Contributions, bug reports, and thoughtful feature suggestions are welcome.

1. Fork the repository.
2. Create a branch for your change.
3. Make your changes.
4. Test the affected functionality.
5. Open a pull request describing what changed and how you tested it.

For major features, consider opening an issue first so the approach can be discussed.

- [Browse open issues](https://github.com/gggff123/J-bot/issues)
- [Request a feature](https://github.com/gggff123/J-bot/issues)
- [Explore the source code](https://github.com/gggff123/J-bot)

## ⭐ Support the project

If J-Bot interests you, here are a few ways to help:

- ⭐ **Star the repository** to bookmark it and show your interest.
- 🐛 Report reproducible bugs.
- 💡 Suggest practical features.
- 🔧 Contribute improvements.
- 📢 Share a real demonstration with developers who may find it useful.

Every useful issue, contribution, and piece of feedback helps the project improve.

## 📜 License

J-Bot is distributed under the [MIT License](LICENSE).

See the `LICENSE` file for the complete terms.

---

<div align="center">

### 🤖 J-Bot

**Think. Use tools. Get things done.**

Built with Python, curiosity, and a lot of experimentation.

[**Explore J-Bot on GitHub**](https://github.com/gggff123/J-bot)

</div>

