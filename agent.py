from lfm import tool, run_agent
from rich.console import Console
import requests
from urllib.parse import quote
import shutil
import os
from dotenv import load_dotenv

try:
    console = Console()
    load_dotenv()

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

    @tool
    def read_file(file: str):
        """
        Read and return the contents of an existing text file.

        file MUST be the actual filename.
        Example: read_file("app.txt")

        Do not use a description such as "the file" or "weather file"
        unless that is literally the filename.
        """
        file_path = os.path.abspath(file)
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                print(line.strip())
        return "Read !"

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
