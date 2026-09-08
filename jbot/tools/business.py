import csv
import io
import os
import smtplib
from email.message import EmailMessage
from jbot.tools.registry import tool


@tool
def read_spreadsheet(file_path: str):
    """
    Read and parse a CSV spreadsheet file, returning its rows as a list of dicts.

    Args:
        file_path: Path to the CSV file.
    """
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' not found."
    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            return {"columns": reader.fieldnames, "row_count": len(rows), "rows": rows[:50]}
    except Exception as e:
        return f"Error reading spreadsheet: {e}"


@tool
def write_csv(file_path: str, data_json: str):
    """
    Write structured data to a CSV spreadsheet file.

    Args:
        file_path: Destination CSV file path.
        data_json: JSON string representing a list of objects/dicts to write.
    """
    import json

    try:
        data = json.loads(data_json)
        if not isinstance(data, list) or not data:
            return "Error: data_json must be a non-empty JSON list of objects."
        keys = list(data[0].keys())
        with open(file_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        return f"Successfully wrote {len(data)} rows to '{file_path}'."
    except Exception as e:
        return f"Error writing CSV: {e}"


@tool
def calculate_roi(initial_investment: float, final_value: float):
    """
    Calculate Return on Investment (ROI) percentage.

    Args:
        initial_investment: The initial amount invested.
        final_value: The final value or return.
    """
    if initial_investment <= 0:
        return "Error: Initial investment must be greater than zero."
    roi = ((final_value - initial_investment) / initial_investment) * 100
    return {
        "initial_investment": initial_investment,
        "final_value": final_value,
        "net_profit": final_value - initial_investment,
        "roi_percent": round(roi, 2),
    }


@tool
def send_email(to_email: str, subject: str, body: str):
    """
    Send an email via SMTP using configuration from environment variables.

    Required environment variables:
    - SMTP_HOST
    - SMTP_PORT (default 587)
    - SMTP_USER
    - SMTP_PASSWORD
    - SMTP_FROM (optional, defaults to SMTP_USER)

    Args:
        to_email: Recipient email address.
        subject: Email subject.
        body: Plain text body of the email.
    """
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM") or user

    if not host or not user or not password:
        return (
            "Error: SMTP configuration missing. Set SMTP_HOST, SMTP_USER, "
            "and SMTP_PASSWORD in your environment / .env file."
        )

    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email

        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=30) as server:
                server.login(user, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=30) as server:
                server.starttls()
                server.login(user, password)
                server.send_message(msg)

        return f"Email successfully sent to {to_email}."
    except Exception as e:
        return f"Failed to send email: {e}"
