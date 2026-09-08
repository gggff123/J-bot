import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
ENV_FILE = ROOT_DIR / ".env"
ENV_EXAMPLE = ROOT_DIR / ".env.example"


def setup_wizard():
    print("==========================================")
    print("        J-BOT SETUP WIZARD")
    print("==========================================")
    print("Configure your LLM provider and API keys.\n")

    if ENV_FILE.exists():
        choice = input(".env file already exists. Overwrite? (y/N): ").strip().lower()
        if choice != "y":
            print("Setup cancelled. Existing .env preserved.")
            return

    print("\nChoose your LLM setup:")
    print("1. Custom / Remote API endpoint (e.g. Inception Labs, OpenAI, Groq, custom)")
    print("2. Local LLM via Ollama / LM Studio (e.g. http://localhost:11434/v1 or http://localhost:1234/v1)")
    
    mode = input("\nEnter choice [1-2] (default 1): ").strip()

    base_url = "https://api.inceptionlabs.ai/v1"
    model = "mercury-2"
    api_key = ""

    if mode == "2":
        print("\nLocal LLM Selected (Make sure Ollama or LM Studio is running).")
        base_url = input("Enter local endpoint base URL [http://localhost:11434/v1]: ").strip() or "http://localhost:11434/v1"
        model = input("Enter model name [llama3]: ").strip() or "llama3"
        api_key = "local-dummy-key"
    else:
        base_url = input("Enter API base URL [https://api.inceptionlabs.ai/v1]: ").strip() or "https://api.inceptionlabs.ai/v1"
        model = input("Enter model name [mercury-2]: ").strip() or "mercury-2"
        api_key = input("Enter your API key: ").strip()

    print("\nOptional API Keys (Press Enter to skip):")
    news_key = input("NewsAPI key (optional): ").strip()
    tinyfish_key = input("TinyFish web search key (optional): ").strip()
    smtp_host = input("SMTP host for business emails (e.g. smtp.gmail.com) (optional): ").strip()
    smtp_port = input("SMTP port [587] (optional): ").strip() or "587"
    smtp_user = input("SMTP user / email (optional): ").strip()
    smtp_pass = input("SMTP password (optional): ").strip()

    env_content = f"""# LLM Configuration
USER_LLM_API_KEY={api_key}
USER_LLM_BASE_URL={base_url}
USER_LLM_MODEL={model}

# Optional Tools
NEWS_API_KEY={news_key}
TINYFISH_KEY={tinyfish_key}

# SMTP Email Configuration
SMTP_HOST={smtp_host}
SMTP_PORT={smtp_port}
SMTP_USER={smtp_user}
SMTP_PASSWORD={smtp_pass}

# Runtime Settings
JBOT_SANDBOX=.
JBOT_MAX_STEPS=8
JBOT_TIMEOUT=60
JBOT_TEMPERATURE=0.2
JBOT_HISTORY_LIMIT=20
"""

    ENV_FILE.write_text(env_content, encoding="utf-8")
    print(f"\nConfiguration saved to {ENV_FILE}")
    print("\nSetup complete! You can now run:")
    print("  python -m jbot")


if __name__ == "__main__":
    setup_wizard()
