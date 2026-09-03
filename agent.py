import needle
import requests
from urllib.parse import quote
import shutil
import os
a=input("What do you want to do?: ")
@needle.tool
#-----------------------------------------
# FILE OPERATIONS
# ----------------------------------------
def create_file(file_name:str,value:str):
    """
        Create a NEW text file.

        IMPORTANT ARGUMENT RULES:
        - file_name MUST be the actual filename/path requested by the user.
          Examples: "app.txt", "notes.txt", "data/output.txt"
        - value MUST be the content that should be written into that file.
        - NEVER put a description such as "weather content", "the answer",
          "output", or "text" into file_name.
        - If the user says "put X into app.txt", then:
            file_name = "app.txt"
            value = X

        USE THIS TOOL ONLY when the destination file does NOT already exist
        or the user explicitly asks to create a new file.

        DO NOT use this tool for:
        - adding to an existing file
        - appending
        - inserting
        - modifying
        - updating
        - replacing part of an existing file

        For multi-step requests, use the result of the previous tool as
        the value for this tool.

        Example:
        User: "Get the weather for Kolkata and put it into app.txt"
        Step 1: call get_weather("Kolkata")
        Step 2: call create_file(
            file_name="app.txt",
            value=<exact result returned by get_weather>
        )
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
@needle.tool
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
@needle.tool
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
@needle.tool
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
@needle.tool
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
@needle.tool
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
@needle.tool
def get_weather(location:str):
    """
    Get the current weather for a location.

    location MUST be a real place name supplied by the user.

    Returns a text result containing:
    - current temperature
    - current wind speed

    Example:
    get_weather("Kolkata")

    IMPORTANT:
    When another tool needs the weather information, use the EXACT
    text returned by this tool as that tool's input.

    Example workflow:
    get_weather("Kolkata")
        -> returns weather text
    create_file("app.txt", <weather text>)
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
@needle.tool
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
# calling others
agent=needle.Needle(tools=[create_file,get_weather,web_search_wikipedia,read_file,open_file,move_file,remove_file,copy_file])
ai_response = agent.run(a)
print(ai_response["results"])
