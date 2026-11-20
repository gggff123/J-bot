from lfm import tool, run_agent
from rich.console import Console
import requests
from urllib.parse import quote
import shutil
import os
from dotenv import load_dotenv, set_key
import platform
import psutil
from github import Github
from github.GithubException import GithubException
import queue
import threading
import subprocess
from pathlib import Path
import uuid
import time

try:
    console = Console()

    env_file = ".env"
    value = input("Enter your GitHub token: ").strip()

    if value:
        set_key(env_file, "GITHUB_TOKEN", value)
        print("GitHub token saved to .env")
    else:
        print("No value entered. Nothing saved.")
    load_dotenv(env_file)
    GIT_TOKEN = os.getenv("GITHUB_TOKEN")

    # ============================================================
    # ONE PERSISTENT WINDOWS CMD PROCESS
    # ============================================================

    _CMD_PROCESS = None
    _CMD_OUTPUT = queue.Queue()
    _CMD_LOCK = threading.Lock()

    def _start_cmd():
        """Start the one reusable CMD process if it is not already alive."""
        global _CMD_PROCESS, _CMD_OUTPUT

        if _CMD_PROCESS is not None and _CMD_PROCESS.poll() is None:
            return

        _CMD_OUTPUT = queue.Queue()
        process = subprocess.Popen(
            ["cmd.exe", "/Q"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        _CMD_PROCESS = process

        def output_reader(proc, output_queue):
            try:
                for line in proc.stdout:
                    output_queue.put(line)
            except (OSError, ValueError):
                pass

        threading.Thread(
            target=output_reader,
            args=(process, _CMD_OUTPUT),
            daemon=True,
        ).start()

        process.stdin.write("chcp 65001>nul\n")
        process.stdin.flush()

    @tool
    def run_command(
        command: str,
        working_directory: str = "",
        timeout_seconds: int = 120,
    ) -> dict:
        """Run a single-line Windows CMD command in one persistent shell.
        The working directory and environment persist between calls.
        A nonzero exit code does not disable later commands."""
        global _CMD_PROCESS

        if os.name != "nt":
            return {"success": False, "error": "This tool supports Windows only."}
        if not command or not command.strip():
            return {"success": False, "error": "Command cannot be empty."}
        if "\n" in command or "\r" in command:
            return {"success": False, "error": "Provide one CMD command per call."}
        if not 1 <= timeout_seconds <= 1800:
            return {
                "success": False,
                "error": "timeout_seconds must be between 1 and 1800.",
            }

        with _CMD_LOCK:
            try:
                _start_cmd()

                if working_directory:
                    directory = Path(working_directory).expanduser().resolve()
                    if not directory.is_dir():
                        return {
                            "success": False,
                            "error": f"Working directory does not exist: {directory}",
                        }
                    _CMD_PROCESS.stdin.write(f'cd /d "{directory}"\n')
                    _CMD_PROCESS.stdin.flush()

                marker = f"__JBOT_EXIT_{uuid.uuid4().hex}__"
                _CMD_PROCESS.stdin.write(command + "\n")
                # A separate input line reads the previous command's exit code.
                _CMD_PROCESS.stdin.write(f"echo {marker}:%errorlevel%\n")
                _CMD_PROCESS.stdin.flush()

                lines = []
                deadline = time.monotonic() + timeout_seconds

                while time.monotonic() < deadline:
                    if _CMD_PROCESS is None or _CMD_PROCESS.poll() is not None:
                        raise RuntimeError("The CMD process terminated unexpectedly.")

                    try:
                        line = _CMD_OUTPUT.get(timeout=0.15)
                    except queue.Empty:
                        continue

                    line = line.rstrip("\r\n")
                    if marker in line:
                        exit_text = line.split(marker, 1)[1].strip()
                        # CMD echo prints MARKER:<exit-code>; remove the delimiter.
                        exit_text = exit_text.lstrip(":").strip()
                        exit_code = int(exit_text)
                        return {
                            "success": exit_code == 0,
                            "exit_code": exit_code,
                            "output": "\n".join(lines)[-30000:],
                            "timed_out": False,
                            "persistent_cmd": True,
                            "message": (
                                "Command completed."
                                if exit_code == 0
                                else "Command failed; CMD remains available for another command."
                            ),
                        }
                    lines.append(line)

                # A timed-out command could still be writing output. Reset the shell
                # to prevent that output being mistaken for the next command's result.
                old_process = _CMD_PROCESS
                _CMD_PROCESS = None
                old_process.kill()
                old_process.wait(timeout=5)
                return {
                    "success": False,
                    "exit_code": None,
                    "output": "\n".join(lines)[-30000:],
                    "timed_out": True,
                    "message": "Command timed out. A fresh persistent CMD starts on the next call.",
                }

            except Exception as exc:
                old_process = _CMD_PROCESS
                _CMD_PROCESS = None
                if old_process is not None:
                    try:
                        if old_process.poll() is None:
                            old_process.kill()
                            old_process.wait(timeout=5)
                    except Exception:
                        pass
                return {
                    "success": False,
                    "error": str(exc),
                    "message": "CMD can restart automatically on the next command.",
                }

    @tool
    def close_cmd() -> dict:
        "Close the persistent cmd when the user asks for it"
        global _CMD_PROCESS
        with _CMD_LOCK:
            if _CMD_PROCESS is None:
                return {"success": True, "message": "No CMD process is running."}
            try:
                if _CMD_PROCESS.poll() is None:
                    _CMD_PROCESS.stdin.write("exit\n")
                    _CMD_PROCESS.stdin.flush()
                    _CMD_PROCESS.wait(timeout=3)
                _CMD_PROCESS = None
                return {"success": True, "message": "Persistent CMD closed."}
            except Exception as exc:
                try:
                    _CMD_PROCESS.kill()
                except Exception:
                    pass
                _CMD_PROCESS = None
                return {"success": False, "error": str(exc)}

    # -----------------------------------------
    # FILE OPERATIONS
    # ----------------------------------------
    @tool
    def create_file(file_name: str, value: str):
        """
        Create a text file.

        Args:
            file_name: The EXACT filename/path where the file must be created.
            value: The EXACT content that must be written into the file.

        IMPORTANT:
            file_name is ALWAYS the destination filename.
            value is ALWAYS the content.

        Example:
            User: "Get weather for Kolkata and put it into weather.txt"

            First:
                get_weather("Kolkata")

            Suppose it returns:
                "It's 31°C in Kolkata right now"

            Then:
                create_file(
                    file_name="weather.txt",
                    value="It's 31°C in Kolkata right now"
                )

        NEVER:
            create_file(
                file_name="weather content",
                value="weather.txt"
            )

        NEVER use descriptions such as:
            "weather content"
            "the answer"
            "the result"
            "weather information"

        as file_name unless the user literally requested that as the filename.
        """
        if os.path.exists(file_name) == True:
            print(f"WARNING | WILL OVERWRITE YOUR EXISTING FILE {file_name} |")
            confirm = input("Confirm (y/n) : ")
            if confirm == "y" or confirm == "Y":
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(value)
                return {"Output": f"Created a file {file_name}"}
            else:
                return "No seleceted so exiting."
        else:
            with open(file_name, "w") as f:
                f.write(value)
            return {"Output": f"Created a file {file_name}"}

    def _repo_path(repository_path):
        repo = Path(repository_path).expanduser().resolve()
        if not repo.is_dir() or not (repo / ".git").exists():
            raise ValueError("The specified directory is not a Git repository.")
        return repo

    @tool
    def read_repo_file(repository_path: str, file_path: str) -> dict:
        "Read repo files"
        try:
            repo = _repo_path(repository_path)
            relative = Path(file_path)
            if relative.is_absolute():
                return {"success": False, "error": "Use a repository-relative path."}
            target = (repo / relative).resolve()
            if not target.is_relative_to(repo):
                return {"success": False, "error": "File path escapes repository."}
            if not target.is_file():
                return {"success": False, "error": "File does not exist."}
            return {
                "success": True,
                "file": str(target),
                "content": target.read_text(encoding="utf-8"),
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    @tool
    def edit_repo_file(repository_path: str, file_path: str, content: str) -> dict:
        "Edit repo files"
        try:
            repo = _repo_path(repository_path)
            relative = Path(file_path)
            if relative.is_absolute():
                return {"success": False, "error": "Use a repository-relative path."}
            target = (repo / relative).resolve()
            if not target.is_relative_to(repo):
                return {"success": False, "error": "File path escapes repository."}
            if target.exists() and target.is_dir():
                return {"success": False, "error": "Target is a directory."}
            existed = target.exists()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return {
                "success": True,
                "action": "updated" if existed else "created",
                "file": str(target),
                "bytes_written": target.stat().st_size,
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    @tool
    def review_repo_diff(repository_path: str) -> dict:
        "Review diff after an edit"
        try:
            repo = _repo_path(repository_path)

            def git(*args):
                result = subprocess.run(
                    ["git", "-C", str(repo), *args],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=45,
                )
                if result.returncode != 0:
                    raise RuntimeError(
                        result.stderr.strip() or f"git exited {result.returncode}"
                    )
                return result.stdout

            status = git("status", "--short")
            unstaged = git("diff", "--no-ext-diff", "--", ".")
            staged = git("diff", "--cached", "--no-ext-diff", "--", ".")
            untracked = git("ls-files", "--others", "--exclude-standard")

            return {
                "success": True,
                "repository": str(repo),
                "status": status[:12000],
                "unstaged_diff": unstaged[:40000],
                "staged_diff": staged[:40000],
                "untracked_files": untracked[:12000],
                "has_changes": bool(status.strip()),
                "truncated": len(unstaged) > 40000 or len(staged) > 40000,
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    @tool
    def read_file(file: str) -> dict:
        "Read all text from an existing text file using its exact path."
        try:
            path = Path(file).expanduser().resolve()
            if not path.is_file():
                return {"success": False, "error": "File does not exist."}
            return {
                "success": True,
                "file": str(path),
                "content": path.read_text(encoding="utf-8"),
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    @tool
    def open_file(file: str):
        """
        Open an existing file using the operating system's default application.

        file MUST be the actual filename.
        Example: open_file("app.txt")

        Do not use this tool to read or modify file contents.
        """
        import os

        file_path = os.path.abspath(file)
        os.startfile(file_path)
        return f"Opened your file: {file}"

    @tool
    def move_file(original_path: str, location: str):
        """
        Move an existing file.

        orignal_path = the current actual file path.
        location = the destination path or directory.

        Example:
        move_file("app.txt", "C:/Users/User/Documents/app.txt")
        """
        shutil.move(original_path, location)
        return f"Moved {original_path} to {location}."

    @tool
    def remove_file(file: str):
        """
        Permanently delete an existing file.

        file MUST be the actual file path.
        Never delete a file unless the user's request clearly asks for deletion.
        """
        file_path = os.path.abspath(file)
        confirm = input(f"WARNING | DELETING FILE : {file_path} (y/n): ")
        if confirm == "y" or confirm == "Y":
            os.remove(file_path)
            return f"Removed file {file} from path {file_path}"
        else:
            return "No selected so exiting.."

    @tool
    def copy_file(file: str, location: str):
        """
        Copy an existing file.

        file = actual source file name
        location = actual destination path or directory.

        Example:
        copy_file("app.txt", "backup/app.txt")
        """
        path = os.path.abspath(file)
        shutil.copy2(path, location)
        return f"File copied from path {path} to {location}"

    # -----------------------------------------
    # WEB SEARCH
    # ----------------------------------------
    @tool
    def get_weather(location: str):
        """Get the current weather for a location."""
        try:
            geo = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={
                    "name": location,
                    "count": 1,
                    "language": "en",
                    "format": "json",
                },
                timeout=10,
            )

            geo.raise_for_status()
            data = geo.json()

            if not data.get("results"):
                return f"Could not find the location: {location}"

            place = data["results"][0]

            latitude = place["latitude"]
            longitude = place["longitude"]

            weather = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                    "timezone": "auto",
                },
                timeout=10,
            )

            weather.raise_for_status()
            current = weather.json()["current"]

            return {
                "location": f"{place['name']}, {place.get('country', '')}",
                "temperature": current["temperature_2m"],
                "feels_like": current["apparent_temperature"],
                "humidity": current["relative_humidity_2m"],
                "wind_speed": current["wind_speed_10m"],
                "weather_code": current["weather_code"],
                "unit": "°C",
            }

        except requests.Timeout:
            return "Weather request timed out."

        except requests.RequestException as e:
            return f"Weather API error: {e}"

        except Exception as e:
            return f"Weather error: {e}"

    @tool
    def web_search(query: str):
        """Search the web and fetch the most relevant result."""
        try:
            api_key = os.getenv("TINYFISH_API_KEY")

            if not api_key:
                api_key = console.input(
                    "[bold yellow]Enter your TinyFish API key: [/bold yellow]"
                ).strip()

                if not api_key:
                    return "No TinyFish API key provided."

                with open(".env", "a", encoding="utf-8") as f:
                    f.write(f"\nTINYFISH_API_KEY={api_key}\n")

                os.environ["TINYFISH_API_KEY"] = api_key

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            }

            search_response = requests.get(
                "https://api.tinyfish.ai/v1/search",
                params={"query": query},
                headers=headers,
                timeout=20,
            )

            search_response.raise_for_status()
            search_data = search_response.json()

            results = search_data.get("results", [])

            if not results:
                return f"No search results found for: {query}"

            first_result = results[0]

            url = first_result.get("url")

            if not url:
                return first_result

            fetch_response = requests.post(
                "https://api.tinyfish.ai/v1/fetch",
                headers={**headers, "Content-Type": "application/json"},
                json={"url": url},
                timeout=30,
            )

            fetch_response.raise_for_status()

            return {
                "query": query,
                "title": first_result.get("title"),
                "url": url,
                "content": fetch_response.json(),
            }

        except requests.Timeout:
            return "Web search timed out."

        except requests.HTTPError as e:
            return f"Web search HTTP error: {e}"

        except requests.RequestException as e:
            return f"Web search request failed: {e}"

        except Exception as e:
            return f"Web search error: {e}"

    # --------------
    # System tools
    # ------------
    @tool
    def open_application(app_name: str):
        """Use tool to open a application for eg : if users tells to open notepad give args notepad
        ARGS : app_name
        """
        os.startfile(app_name + ".exe")
        return f"Opened {app_name}"

    # ----------------
    # github tools
    # ----------------
    @tool
    def github_user(username: str):
        """Get detailed public information about a GitHub user. Use when the user asks about a GitHub username, profile, account, followers, following, public repositories, bio, location, company, website, or account statistics."""
        url = "https://api.github.com/users/" + username
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            return {"error": f"GitHub user '{username}' was not found."}

        if response.status_code != 200:
            return {
                "error": f"GitHub API request failed with status {response.status_code}"
            }
        user_json = response.json()
        name = user_json["login"]
        avatar = user_json["avatar_url"]
        bio = user_json["bio"]
        repo = user_json["public_repos"]
        followers = user_json["followers"]
        following = user_json["following"]
        return {
            "Name": name,
            "Avatar": avatar,
            "Bio": bio,
            "No_of_repos": repo,
            "Followers": followers,
            "Following": following,
        }

    @tool
    def github_users_repos(username: str):
        """Get a list of repositories owned by a GitHub user. Use when the user asks what projects/repositories a user has, their repositories, or wants to inspect a user's projects."""
        url = f"https://api.github.com/users/{username}/repos"
        res = requests.get(url, timeout=10)
        names = res.json()
        repos = [
            {"name": repo["name"], "description": repo["description"]} for repo in names
        ]
        return {"Repos": repos}

    @tool
    def github_search(query: str, search_type: str = "repositories"):
        """
        Search GitHub for repositories, users, issues, or code.

        Args:
            query: What to search for.
            search_type: One of "repositories", "users", "issues", or "code".
        """

        url = f"https://api.github.com/search/{search_type}"

        response = requests.get(url, params={"q": query, "per_page": 10}, timeout=10)

        if response.status_code != 200:
            return {"error": f"GitHub API request failed: {response.status_code}"}

        data = response.json()

        results = data.get("items", [])

        if search_type == "repositories":
            return [
                {
                    "name": repo.get("full_name"),
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                    "stars": repo.get("stargazers_count"),
                    "url": repo.get("html_url"),
                }
                for repo in results
            ]

        if search_type == "users":
            return [
                {
                    "username": user.get("login"),
                    "avatar": user.get("avatar_url"),
                    "url": user.get("html_url"),
                }
                for user in results
            ]

        if search_type == "issues":
            return [
                {
                    "title": issue.get("title"),
                    "repository": issue.get("repository_url"),
                    "url": issue.get("html_url"),
                    "state": issue.get("state"),
                }
                for issue in results
            ]

        if search_type == "code":
            return [
                {
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "repository": item.get("repository", {}).get("full_name"),
                    "url": item.get("html_url"),
                }
                for item in results
            ]

        return {"error": "Invalid search_type"}

    @tool
    def github_followers(username: str):
        url = f"https://api.github.com/users/{username}/followers"
        res = requests.get(url, timeout=10)
        store = res.json()
        name = [names["login"] for names in store]
        return {"names": name}

    @tool
    def get_issue_comments(owner: str, repo_name: str, issue: int):

        url = (
            f"https://api.github.com/repos/{owner}/{repo_name}/issues/{issue}/comments"
        )

        res = requests.get(url, timeout=10)

        store = res.json()

        print(type(res))
        print(res)

        comments = []

        for comment in store:
            comments.append(
                {
                    "User": comment["user"]["login"],
                    "Comment": comment["body"],
                    "URL": comment["html_url"],
                    "Separator": "-" * 50,
                }
            )
        return comments

    @tool
    def github_issues(owner: str, repo: str):
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        res = requests.get(url, timeout=10)
        a = res.json()
        issues = []
        for item in a:
            issues.append(
                {
                    "Issue_no.": item["number"],
                    "url": item["url"],
                    "title": item["title"],
                    "state": item["state"],
                }
            )
        return issues

    def get_github(token: str = None):
        """Create a GitHub client using the authenticated user's token."""
        token = token or GIT_TOKEN

        if not token:
            raise ValueError("GITHUB_TOKEN is not configured.")

        return Github(token)

    @tool
    def github_get_pull_request(token: str, repository: str, pr_number: int) -> dict:
        """Inspect a pull request."""
        try:
            gh = get_github(token)
            pr = gh.get_repo(repository).get_pull(pr_number)
            return {
                "number": pr.number,
                "title": pr.title,
                "body": pr.body or "",
                "state": pr.state,
                "author": pr.user.login,
                "head": pr.head.ref,
                "base": pr.base.ref,
                "url": pr.html_url,
            }
        except GithubException as e:
            return {"error": str(e)}

    @tool
    def github_comment_on_pr(
        token: str, repository: str, pr_number: int, comment: str
    ) -> dict:
        """Post a conversation comment on a pull request."""
        try:
            gh = get_github(token)
            pr = gh.get_repo(repository).get_pull(pr_number)
            result = pr.create_issue_comment(comment)
            return {"success": True, "comment_id": result.id, "url": result.html_url}
        except GithubException as e:
            return {"error": str(e)}

    def format_github_comment(comment: str) -> str:
        comment = comment.strip()
        if not comment:
            raise ValueError("Comment cannot be empty.")

        signature = (
            "---\n\n"
            "<sub>🤖 Generated by **J-Bot** · "
            "AI-assisted GitHub maintenance</sub>"
        )

        if "Generated by **J-Bot**" in comment:
            return comment
        return f"{comment}\n\n{signature}"

    @tool
    def github_comment_on_issue(
        repository: str, issue_number: int, comment: str
    ) -> dict:
        "Post a comment on a GitHub issue. Automatically appends the J-Bot signature."
        try:
            issue = get_github().get_repo(repository).get_issue(issue_number)
            result = issue.create_comment(format_github_comment(comment))
            return {
                "success": True,
                "type": "issue",
                "number": issue_number,
                "comment_id": result.id,
                "url": result.html_url,
            }
        except (GithubException, ValueError) as exc:
            return {"success": False, "error": str(exc)}

    def github_error(exc):
        return {"success": False, "error": str(exc)}

    @tool
    def github_react_to_issue(
        repository: str,
        issue_number: int,
        reaction: str,
    ) -> dict:
        """Add a GitHub reaction to an issue or pull request.
        Allowed reactions: +1, -1, laugh, confused, heart, hooray, rocket, eyes."""
        try:
            allowed = {
                "+1",
                "-1",
                "laugh",
                "confused",
                "heart",
                "hooray",
                "rocket",
                "eyes",
            }
            if reaction not in allowed:
                return {
                    "success": False,
                    "error": f"Invalid reaction. Choose from {sorted(allowed)}.",
                }
            issue = get_github().get_repo(repository).get_issue(issue_number)
            result = issue.create_reaction(reaction)
            return {
                "success": True,
                "reaction": reaction,
                "issue_number": issue_number,
                "reaction_id": result.id,
            }
        except GithubException as exc:
            return github_error(exc)

    @tool
    def github_react_to_comment(
        repository: str,
        comment_id: int,
        reaction: str,
    ) -> dict:
        """Add a reaction to a specific GitHub issue or PR comment.
        Requires the comment database ID, not the issue number."""
        try:
            allowed = {
                "+1",
                "-1",
                "laugh",
                "confused",
                "heart",
                "hooray",
                "rocket",
                "eyes",
            }
            if reaction not in allowed:
                return {
                    "success": False,
                    "error": f"Invalid reaction. Choose from {sorted(allowed)}.",
                }
            repo = get_github().get_repo(repository)
            result = repo.get_issue_comment(comment_id).create_reaction(reaction)
            return {
                "success": True,
                "reaction": reaction,
                "comment_id": comment_id,
                "reaction_id": result.id,
            }
        except GithubException as exc:
            return github_error(exc)

    @tool
    def github_add_issue_labels(
        repository: str, issue_number: int, labels: list[str]
    ) -> dict:
        "Add one or more existing GitHub labels to an issue. Labels must already exist in the repository."
        try:
            if not labels:
                return {"success": False, "error": "Provide at least one label."}
            issue = get_github().get_repo(repository).get_issue(issue_number)
            issue.add_to_labels(*labels)
            return {
                "success": True,
                "issue_number": issue_number,
                "labels": [label.name for label in issue.labels],
                "url": issue.html_url,
            }
        except GithubException as exc:
            return github_error(exc)

    @tool
    def github_create_label(
        repository: str,
        name: str,
        color: str,
        description: str = "",
    ) -> dict:
        "Create a label in a GitHub repository."
        try:
            color = color.lstrip("#")
            if len(color) != 6 or any(
                ch not in "0123456789abcdefABCDEF" for ch in color
            ):
                return {
                    "success": False,
                    "error": "Color must be six hexadecimal characters, e.g. 1D76DB.",
                }
            label = (
                get_github()
                .get_repo(repository)
                .create_label(
                    name=name,
                    color=color,
                    description=description,
                )
            )
            return {
                "success": True,
                "name": label.name,
                "color": label.color,
                "url": label.url,
            }
        except GithubException as exc:
            return github_error(exc)

    @tool
    def github_remove_issue_label(
        repository: str, issue_number: int, label: str
    ) -> dict:
        "Remove a label from a GitHub issue."
        try:
            issue = get_github().get_repo(repository).get_issue(issue_number)
            issue.remove_from_labels(label)
            return {
                "success": True,
                "issue_number": issue_number,
                "remaining_labels": [item.name for item in issue.labels],
            }
        except GithubException as exc:
            return github_error(exc)

    @tool
    def github_create_branch(
        token: str, repository: str, branch_name: str, base_branch: str
    ) -> dict:
        """Create a branch from an existing branch."""
        try:
            gh = get_github(token)
            repo = gh.get_repo(repository)
            base = repo.get_branch(base_branch)
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base.commit.sha,
            )
            return {"success": True, "branch": branch_name}
        except GithubException as e:
            return {"error": str(e)}

    @tool
    def github_push_changes(
        token: str,
        repository: str,
        branch_name: str,
        commit_message: str,
        files: dict[str, str],
    ) -> dict:
        """Create a commit and push text file changes to an existing branch.

        files maps repository-relative paths to complete file contents.
        Existing files are replaced; new files are created.
        """
        try:
            gh = get_github(token)
            repo = gh.get_repo(repository)
            ref = repo.get_git_ref(f"heads/{branch_name}")
            parent = repo.get_git_commit(ref.object.sha)

            tree_items = []
            for path, content in files.items():
                if (
                    not path
                    or path.startswith("/")
                    or "\\" in path
                    or any(p in ("", ".", "..") for p in path.split("/"))
                ):
                    return {"error": f"Invalid file path: {path}"}

                blob = repo.create_git_blob(content, "utf-8")
                tree_items.append(
                    {
                        "path": path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob.sha,
                    }
                )

            tree = repo.create_git_tree(tree_items, parent.tree)
            commit = repo.create_git_commit(commit_message, tree, [parent])

            # Avoid overwriting concurrent changes.
            current_ref = repo.get_git_ref(f"heads/{branch_name}")
            if current_ref.object.sha != parent.sha:
                return {"error": "Branch changed concurrently; retry after reviewing."}

            current_ref.edit(commit.sha, force=False)

            return {
                "success": True,
                "commit_sha": commit.sha,
                "commit_url": commit.html_url,
                "branch": branch_name,
                "files_changed": list(files.keys()),
            }
        except GithubException as e:
            return {"error": str(e)}

    @tool
    def github_create_pull_request(
        token: str,
        repository: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str,
        draft: bool = False,
    ) -> dict:
        """Create a pull request from a head branch into a base branch."""
        try:
            if head_branch == base_branch:
                return {"error": "Head and base branches must differ."}

            gh = get_github(token)
            repo = gh.get_repo(repository)

            pr = repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch,
                draft=draft,
            )

            return {
                "success": True,
                "number": pr.number,
                "title": pr.title,
                "url": pr.html_url,
            }
        except GithubException as e:
            return {"error": str(e)}

    @tool
    def github_create_issue(
        repository: str,
        title: str,
        body: str,
    ) -> dict:
        """Create an issue in a repository. Repository format: owner/repo."""
        try:
            gh = get_github(GIT_TOKEN)
            repo = gh.get_repo(repository)

            issue = repo.create_issue(title=title, body=body)

            return {
                "success": True,
                "number": issue.number,
                "title": issue.title,
                "url": issue.html_url,
            }

        except GithubException as e:
            return {"success": False, "error": str(e)}

    @tool
    def github_close_issue(repository: str, issue_number: int) -> dict:
        """Close an existing GitHub issue."""
        try:
            gh = get_github(GIT_TOKEN)
            repo = gh.get_repo(repository)
            issue = repo.get_issue(issue_number)

            issue.edit(state="closed")

            return {
                "success": True,
                "action": "closed",
                "number": issue.number,
                "url": issue.html_url,
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}

    @tool
    def github_reopen_issue(repository: str, issue_number: int) -> dict:
        """Reopen a previously closed GitHub issue."""
        try:
            gh = get_github(GIT_TOKEN)
            repo = gh.get_repo(repository)
            issue = repo.get_issue(issue_number)

            issue.edit(state="open")

            return {
                "success": True,
                "action": "reopened",
                "number": issue.number,
                "url": issue.html_url,
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}

    @tool
    def github_close_pr(repository: str, pr_number: int) -> dict:
        """Close an existing pull request without merging it."""
        try:
            gh = get_github(GIT_TOKEN)
            repo = gh.get_repo(repository)
            pr = repo.get_pull(pr_number)

            pr.edit(state="closed")

            return {
                "success": True,
                "action": "closed",
                "number": pr.number,
                "url": pr.html_url,
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}

    @tool
    def github_reopen_pr(repository: str, pr_number: int) -> dict:
        """Reopen a previously closed pull request."""
        try:
            gh = get_github(GIT_TOKEN)
            repo = gh.get_repo(repository)
            pr = repo.get_pull(pr_number)

            pr.edit(state="open")

            return {
                "success": True,
                "action": "reopened",
                "number": pr.number,
                "url": pr.html_url,
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}

    @tool
    def github_merge_pr(
        repository: str,
        pr_number: int,
        merge_method: str = "merge",
        commit_message: str = "",
    ) -> dict:
        """
        Merge a pull request.
        merge_method must be merge, squash, or rebase.
        """
        try:
            if merge_method not in ("merge", "squash", "rebase"):
                return {
                    "success": False,
                    "error": "Invalid merge method. Use merge, squash, or rebase.",
                }

            gh = get_github(GIT_TOKEN)
            repo = gh.get_repo(repository)
            pr = repo.get_pull(pr_number)

            if pr.merged:
                return {
                    "success": False,
                    "error": "This pull request is already merged.",
                }

            if pr.state != "open":
                return {
                    "success": False,
                    "error": "Cannot merge a closed pull request.",
                }

            result = pr.merge(
                commit_message=commit_message or None, merge_method=merge_method
            )

            return {
                "success": result.merged,
                "merged": result.merged,
                "message": result.message,
                "sha": result.sha,
                "number": pr_number,
                "url": pr.html_url,
            }

        except GithubException as e:
            return {"success": False, "error": str(e)}

    @tool
    def github_close_issue_duplicate(
        repository: str, issue_number: int, duplicate_of: int = 0
    ) -> dict:
        "Close a GitHub issue as a duplicate, optionally linking the original issue number."
        return _close_github_item(
            repository, issue_number, "issue", "duplicate", duplicate_of
        )

    @tool
    def github_close_issue_stale(repository: str, issue_number: int) -> dict:
        "Close a GitHub issue as stale due to inactivity."
        return _close_github_item(repository, issue_number, "issue", "stale", 0)

    @tool
    def github_close_pr_duplicate(
        repository: str, pr_number: int, duplicate_of: int = 0
    ) -> dict:
        "Close a GitHub pull request as a duplicate, optionally linking the original issue or PR number."
        return _close_github_item(
            repository, pr_number, "pull_request", "duplicate", duplicate_of
        )

    @tool
    def github_close_pr_stale(repository: str, pr_number: int) -> dict:
        "Close a GitHub pull request as stale due to inactivity."
        return _close_github_item(repository, pr_number, "pull_request", "stale", 0)

    def _close_github_item(repository, number, item_type, reason, duplicate_of=0):
        try:
            repo = get_github().get_repo(repository)
            item = (
                repo.get_issue(number)
                if item_type == "issue"
                else repo.get_pull(number)
            )

            if item.state == "closed":
                return {"success": False, "error": "Item is already closed."}

            if reason == "duplicate":
                if duplicate_of:
                    original = repo.get_issue(duplicate_of)
                    message = (
                        f"This is being closed as a duplicate of "
                        f"[#{duplicate_of}]({original.html_url}).\n\n"
                        "Please continue the discussion in the original."
                    )
                else:
                    message = "This is being closed as a duplicate. Please refer to the existing discussion."
            elif reason == "stale":
                message = (
                    "This is being closed as stale due to inactivity. "
                    "If this is still relevant, please reopen it or provide an update."
                )
            else:
                return {"success": False, "error": "Invalid close reason."}

            comment = item.create_comment(format_github_comment(message))
            if item_type == "issue":
                item.edit(state="closed", state_reason="not_planned")
            else:
                item.edit(state="closed")

            return {
                "success": True,
                "number": number,
                "type": item_type,
                "reason": reason,
                "comment_url": comment.html_url,
                "url": item.html_url,
            }
        except (GithubException, ValueError) as exc:
            return {"success": False, "error": str(exc)}

    # ----------------
    # other tools
    # ----------------
    @tool
    def advice():
        """Return an advice if the user asks for it"""
        url = "https://api.adviceslip.com/advice"
        res = requests.get(url)
        a = res.json()
        return {"Advice": a["slip"]["advice"]}

    current_dir = "."
    disk_info = shutil.disk_usage(current_dir)
    disk_available = disk_info.free / (1024**3)
    disk_total = disk_info.total / (1024**3)
    ram_info = psutil.virtual_memory()
    ram_total = ram_info.total / (1024**3)
    ram_available = ram_info.available / (1024**3)

    @tool
    def system_info():
        return {
            "Machine": platform.machine(),
            "OS": platform.system(),
            "Platform": platform.platform(),
            "Processor": platform.processor(),
            "Disk Space total": disk_total,
            "Disk Space Free": disk_available,
            "RAM total": ram_total,
            "RAM available": ram_available,
        }

    # CLI Intro art
    with open("jarvis.txt", encoding="utf-8") as f:
        print(f.read())
        while True:
            user_input = console.input("[bold cyan]What do you want to do?: ")
            if user_input == "/exit" or user_input == "/quit":
                console.print("\n[red bold]quitting...")
                break
            elif user_input == "/tool" or user_input == "/t":
                console.print("""
                    [green bold][   Available tools  ][/green bold]
                    [red]
                    󠁯•󠁏󠁏 Create file | (requires Exact file path)
                    󠁯•󠁏󠁏 Read file | (requires Exact file path)
                    󠁯•󠁏󠁏 Open the file in the default app | (requires Exact file path)
                    󠁯•󠁏󠁏 Move file | (requires Exact file path)
                    󠁯•󠁏󠁏 Remove file | (requires Exact file path)
                    󠁯•󠁏󠁏 Copy file | (requires Exact file path)
                    󠁯•󠁏󠁏 Weather for a location | (give name of state)
                    󠁯•󠁏󠁏 Web search | (requires tinyfish api key)
                    󠁯•󠁏󠁏 Open application (requires app name with .exe)
                    󠁯•󠁏󠁏 Github tools (get info about repo , user , search etc)
                    󠁯•󠁏󠁏 Advice (Gives harmless advices)
                    """)
            else:
                run_agent(user_input, on_token=lambda t: print(t, end="", flush=True))
except KeyboardInterrupt:
    console.print("\n[red bold]quitting...")
