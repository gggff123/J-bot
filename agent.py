from lfm import tool,run_agent
import requests
from urllib.parse import quote
import shutil
import os
from dotenv import load_dotenv
load_dotenv()
#-----------------------------------------
# FILE OPERATIONS
# ----------------------------------------
@tool
def create_file(file_name:str,value:str):
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
    if os.path.exists(file_name)==True:
        print(f"WARNING | WILL OVERWRITE YOUR EXISTING FILE {file_name} |")
        confirm=input("Confirm (y/n) : ")
        if confirm=="y" or confirm== "Y":
            with open(file_name,"w") as f:
                f.write(value)
            return{
                "Output":f"Created a file {file_name}"
            }
        else:
            return "No seleceted so exiting."
    else:
        with open(file_name,"w") as f:
            f.write(value)
        return{
            "Output":f"Created a file {file_name}"
        }
@tool
def read_file(file:str):
    """
    Read and return the contents of an existing text file.

    file MUST be the actual filename/path.
    Example: read_file("app.txt")

    Do not use a description such as "the file" or "weather file"
    unless that is literally the filename.
    """
    with open(file,"r") as f:
        for line in f:
            print(line.strip())
    return "Read !"
@tool
def open_file(file:str):
    """
    Open an existing file using the operating system's default application.

    file MUST be the actual filename/path.
    Example: open_file("app.txt")

    Do not use this tool to read or modify file contents.
    """
    import os
    os.startfile(file)
    return f"Opened your file: {file}"
@tool
def move_file(orignal_path:str,location:str):
    """
    Move an existing file.

    orignal_path = the current actual file path.
    location = the destination path or directory.

    Example:
    move_file("app.txt", "C:/Users/User/Documents/app.txt")
    """
    shutil.move(orignal_path,location)
    return  f"Moved {orignal_path} to {location}."
@tool
def remove_file(file_path:str):
    """
        Permanently delete an existing file.

        file_path MUST be the actual file path.
        Never delete a file unless the user's request clearly asks for deletion.
    """
    confirm=input(f"WARNING | DELETING FILE : {file_path} (y/n): ")
    if confirm == "y" or confirm== "Y":
        os.remove(file_path)
        return f"Removed file from path {file_path}"
    else:
        return f"No selected so exiting.."
@tool
def copy_file(path:str,location:str):
    """
    Copy an existing file.

    path = actual source file path.
    location = actual destination path or directory.

    Example:
    copy_file("app.txt", "backup/app.txt")
    """
    shutil.copy2(path,location)
    return f"File copied from path {path} to {location}"
#-----------------------------------------
# SEARCH
# ----------------------------------------
@tool
def get_weather(location:str):
    """
        Get the current weather for a location.

        Args:
            location: The actual place name requested by the user.

        IMPORTANT:
            Return the weather information as the tool result.

            If another tool needs this information, that tool MUST receive
            the actual result returned by get_weather.

        Example:

            get_weather("Kolkata")

            returns:
            "It's 31°C in Kolkata right now"

            The next tool should receive exactly:
            "It's 31°C in Kolkata right now"
        """
    url=f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
    result=requests.get(url)
    a=result.json()
    latitude=a["results"][0]["latitude"]
    longitude=a["results"][0]["longitude"]
    url_weather=f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m"
    weather=requests.get(url_weather)
    b=weather.json()
    temp=b['current']['temperature_2m']
    wind=b['current']['wind_speed_10m']
    return f"its {temp}°C in {location} right now , with a wind speed of about {wind}km/h"
@tool
def web_search(query:str):
    api_key=os.getenv("tinyfish_key")
    if not api_key:
        print("| API KEY NOT FOUND |")
        confirm=input("Continue (y/n) : ")
        if confirm == "y" or confirm == "Y":
            print("Yes option selected")
            input_api_key=input("Enter your tinyfish api key for web search (https://agent.tinyfish.ai/): ")
            with open(".env","w") as f:
                f.write(f"tinyfish_key='{input_api_key}'")
        else:
            print("Selected No so exiting")
            return "No api key provided"
    else:
        url="https://agent.tinyfish.ai/v1/search"
        headers={
            "X-API-Key":api_key
        }
        response_url=requests.get(url,headers=headers,params={"query":query})
        url_generated=response_url.json()
        url=url_generated["results"][0]["url"]
        fetch = requests.post(
                "https://agent.tinyfish.ai/v1/fetch",
                headers=headers,
                json={
                    "urls": [url]
                }
            )
        return fetch.json()
@tool
def open_application(app_name:str):
    """Use tool to open a application for eg : if users tells to open notepad give args notepad.exe"""
    os.startfile(app_name)
    return f"Opened {app_name}"
@tool
def github_user(username:str):
    """Get detailed public information about a GitHub user. Use when the user asks about a GitHub username, profile, account, followers, following, public repositories, bio, location, company, website, or account statistics."""
    url="https://api.github.com/users/"+username
    response=requests.get(url,timeout=10)
    if response.status_code == 404:
           return {"error": f"GitHub user '{username}' was not found."}

    if response.status_code != 200:
           return {
               "error": f"GitHub API request failed with status {response.status_code}"
           }
    user_json=response.json()
    name=user_json["login"]
    avatar=user_json["avatar_url"]
    bio=user_json["bio"]
    repo=user_json["public_repos"]
    followers=user_json["followers"]
    following=user_json["following"]
    return {
        "Name":name,
        "Avatar":avatar,
        "Bio":bio,
        "No_of_repos":repo,
        "Followers":followers,
        "Following":following
    }
@tool
def github_users_repos(username:str):
    """Get a list of repositories owned by a GitHub user. Use when the user asks what projects/repositories a user has, their repositories, or wants to inspect a user's projects."""
    url=f"https://api.github.com/users/{username}/repos"
    res=requests.get(url)
    names=res.json()
    repos = [
        {
            "name": repo["name"],
            "description": repo["description"]
        }
        for repo in names
    ]
    return repos
@tool
def github_search(query: str, search_type: str = "repositories"):
        """
        Search GitHub for repositories, users, issues, or code.

        Args:
            query: What to search for.
            search_type: One of "repositories", "users", "issues", or "code".
        """

        url = f"https://api.github.com/search/{search_type}"

        response = requests.get(
            url,
            params={"q": query, "per_page": 10},
            timeout=10
        )

        if response.status_code != 200:
            return {
                "error": f"GitHub API request failed: {response.status_code}"
            }

        data = response.json()

        results = data.get("items", [])

        if search_type == "repositories":
            return [
                {
                    "name": repo.get("full_name"),
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                    "stars": repo.get("stargazers_count"),
                    "url": repo.get("html_url")
                }
                for repo in results
            ]

        if search_type == "users":
            return [
                {
                    "username": user.get("login"),
                    "avatar": user.get("avatar_url"),
                    "url": user.get("html_url")
                }
                for user in results
            ]

        if search_type == "issues":
            return [
                {
                    "title": issue.get("title"),
                    "repository": issue.get("repository_url"),
                    "url": issue.get("html_url"),
                    "state": issue.get("state")
                }
                for issue in results
            ]

        if search_type == "code":
            return [
                {
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "repository": item.get("repository", {}).get("full_name"),
                    "url": item.get("html_url")
                }
                for item in results
            ]

        return {"error": "Invalid search_type"}
@tool
def github_followers(username:str):
    url="https://api.github.com/users/novastardev/followers"
    res=requests.get(url)
    store=res.json()
    name=[names["login"] for names in store]
    return name
#CLI Intro art
with open("jarvis.txt", encoding="utf-8") as f:
    print(f.read())
while True:
    user_input=input("What do you want to do?: ")
    if user_input == "exit" or user_input== "quit":
        break
    else:
        response=run_agent(user_input)
