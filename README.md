<div align="center">

# 🤖 J-bot

### An AI agent that can think, use tools, and get things done.

**J-bot is an extensible Python AI assistant built around tool calling — giving an AI model the ability to interact with the real world.**

<br>

[![GitHub](https://img.shields.io/github/stars/gggff123/J-bot?style=for-the-badge\&logo=github)](https://github.com/gggff123/J-bot)
[![GitHub issues](https://img.shields.io/github/issues/gggff123/J-bot?style=for-the-badge)](https://github.com/gggff123/J-bot/issues)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge\&logo=python\&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-in%20development-orange?style=for-the-badge)]()

<br><br>

**[⭐ Star the repo](https://github.com/gggff123/J-bot) · [🐛 Report a bug](https://github.com/gggff123/J-bot/issues) · [💡 Request a feature](https://github.com/gggff123/J-bot/issues)**

</div>

---

## ⚡ What is J-bot?

J-bot is an experimental **AI agent framework/assistant** designed to give language models access to tools.

Instead of simply generating text, J-bot can decide when it needs an external capability, call a tool, receive the result, and use that information to produce a response.

```text
                    ┌──────────────┐
                    │     USER     │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   J-BOT 🧠   │
                    │     AGENT    │
                    └──────┬───────┘
                           │
                    ┌──────┴──────┐
                    │             │
                Need tool?     No tool
                    │             │
                    ▼             ▼
             ┌────────────┐   ┌─────────┐
             │    TOOL    │   │ RESPONSE│
             └─────┬──────┘   └─────────┘
                   │
                   ▼
              TOOL RESULT
                   │
                   ▼
              ┌─────────┐
              │ J-BOT 🧠│
              └────┬────┘
                   │
                   ▼
                RESPONSE
```

---

## ✨ Features

### 🧠 Agentic AI

J-bot doesn't need every capability built directly into the model.

It can use tools to extend what the model is capable of doing.

### 🔧 Tool Calling

Tools are the core of J-bot.

New capabilities can be added without rebuilding the entire assistant.

### 🔎 Information Retrieval

J-bot can retrieve information from external sources such as Wikipedia.

### 📝 Summarization

Retrieved information can be processed and summarized before being presented to the user.

### 🧩 Extensible

The goal is to make adding a new capability as simple as creating another tool.

---

## 🛠️ Tools

| Tool                  | Status |
| :-------------------- | :----: |
| 🌐 Web Search         |    ✅  |
| 🌦️ Weather           |     ✅  |
| ![GitHub Octocat](https://githubassets.com)  Automation          |   🟡   |
| 🧮 Calculator         |   🚧   |
| 📁 File Operations    |   ✅   |
| 💻 System Information |   🚧   |
| ⏰ Automation          |   🚧   |

> More tools are being added as J-bot evolves.

---

## 🎯 Why J-bot?

Most simple chatbots follow:

```text
User → Model → Response
```

J-bot aims for:

```text
User
 ↓
Agent
 ↓
Understand the task
 ↓
Choose a tool
 ↓
Execute
 ↓
Observe result
 ↓
Reason again
 ↓
Respond
```

This makes the assistant much more than a simple chatbot.

---

## 🚀 Quick Start

### Requirements

* Python 3.x
* Git
* An AI model/API supported by your configuration

### Clone

```bash
git clone https://github.com/gggff123/J-bot.git
cd J-bot
```

### Create a virtual environment

**Windows**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Start J-bot

```powershell
python agent.py
```

---

## 💬 Example

```text
What do you want to do?: Search about Egypt
```

J-bot can determine that external information is required, call the appropriate search tool, retrieve the information, and return the result.

```text
User
  │
  │  Search about Egypt
  ▼
J-bot 🧠
  │
  │  Wikipedia Search
  ▼
Wikipedia 🔎
  │
  │  Article information
  ▼
J-bot 🧠
  │
  ▼
Response
```

---

## 🧱 Architecture

J-bot is being built around a modular architecture:

```text
J-bot
│
├── 🧠 Agent
│
├── 🔧 Tools
│   ├── Wikipedia
│   ├── Web Search
│   └── ...
│
├── ⚙️ Model
│
└── 🖥️ Interface
```

The architecture is intentionally evolving as new capabilities are added.

---
### Tools

* [x] Web search
* [x] Weather
* [ ] Calculator
* [x] File management
* [ ] System information
* [ ] More APIs

### Future

* [ ] Memory
* [ ] Long-running tasks
* [ ] Scheduled tasks
* [ ] Voice interaction
* [ ] Better UI
* [ ] Plugin system
* [ ] Autonomous workflows

---

## 🧪 Development Status

> **J-bot is currently experimental.**

This project is actively being developed and is **not production-ready**.

The architecture, APIs, tools, and behavior may change significantly.

Expect bugs. Expect changes. Expect new features.

That's part of the project.

---

## 🤝 Contributing

Have an idea for a tool?

Found a bug?

Want to improve J-bot?

Contributions are welcome.

```text
Fork
  ↓
Create a branch
  ↓
Make your changes
  ↓
Test
  ↓
Pull Request
```

Before submitting a large change, opening an issue to discuss it is recommended.

---

## ⭐ Support the Project

If you like the idea behind J-bot:

**⭐ Star the repository**

It helps the project get discovered and motivates continued development.

You can also:

* 🐛 Report bugs
* 💡 Suggest features
* 🔧 Contribute code
* 📢 Share the project

---

## 📜 License

License information will be added as the project develops.

---

<div align="center">

### 🤖 J-bot

**Think. Use tools. Get things done.**

Built with Python 🐍

<br>

**[GitHub](https://github.com/gggff123/J-bot)**

</div>

# Honourable Mentions
-- @tomthecatto (Thanks)
