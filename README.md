<div align="center">

# 🤖 J-bot

### An AI agent that can think, use tools, and get things done.

**J-bot is an extensible Python AI assistant built around tool calling — giving an AI model the ability to interact with the real world.**

<br>

[![GitHub](https://img.shields.io/github/stars/gggff123/J-bot?style=for-the-badge&logo=github)](https://github.com/gggff123/J-bot)
[![GitHub issues](https://img.shields.io/github/issues/gggff123/J-bot?style=for-the-badge)](https://github.com/gggff123/J-bot/issues)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-active-brightgreen?style=for-the-badge)]()

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