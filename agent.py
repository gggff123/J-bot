from lfm import tool,run_agent
import requests
from urllib.parse import quote
import shutil
import os
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
def web_search_wikipedia(qu:str):
    """Searches for an object . DO THIS ONLY FOR NAMES , PLACES , ITEM"""
    headers = {
        "User-Agent": "J-bot/1.0 (https://github.com/gggff123/J-bot)",
        "Accept-Encoding": "gzip",
    }

    # Search Wikipedia
    query = quote(qu)

    search_url = (
        f"https://en.wikipedia.org/w/api.php"
        f"?action=opensearch"
        f"&search={query}"
        f"&limit=5"
        f"&format=json"
    )

    search_response = requests.get(
        search_url,
        headers=headers,
        timeout=10
    )
    search_response.raise_for_status()

    search_data = search_response.json()

    titles = search_data[1]
    urls = search_data[3]

    # Take the first result
    title = titles[0]

    # Get article extract
    api_url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "titles": title,
        "format": "json",
    }

    article_response = requests.get(
        api_url,
        params=params,
        headers=headers,
        timeout=10
    )

    article_response.raise_for_status()

    article_data = article_response.json()

    pages = article_data["query"]["pages"]

    page = next(iter(pages.values()))
    article=page.get("extract", "No extract found.")

    return article
@tool
def open_application(app_name:str):
    """Use tool to open a application for eg : if users tells to open notepad give args notepad.exe"""
    os.startfile(app_name)
    return f"Opened {app_name}"
#CLI Intro art
with open("jarvis.txt", encoding="utf-8") as f:
    print(f.read())
while True:
    user_input=input("What do you want to do?: ")
    if user_input == "exit" or user_input== "quit":
        break
    else:
        response=run_agent(user_input)
