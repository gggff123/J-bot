import needle
import requests
from urllib.parse import quote
import shutil
import os
a=input("What do you want to do?: ")
@needle.tool
def create_file(file_name:str,value:str):
    """"ONLY use this tool when the user explicitly wants to CREATE A NEW FILE.
        NEVER use this tool when the user says add, append, insert, modify, update,
        or write something into an EXISTING file."""
    with open(file_name,"w") as f:
        f.write(value)
    return{
        "Output":f"Created a file {file_name}"
    }
@needle.tool
def read_file(file:str):
    """Reads text file"""
    with open(file,"r") as f:
        for line in f:
            print(line.strip())
    return "Read !"
@needle.tool
def open_file(file:str):
    """Open a file in the designated app"""
    import os
    os.startfile(file)
    return f"Opened your file: {file}"
@needle.tool
def move_file(orignal_path:str,location:str):
    """Moves a file from the original location to the final location"""
    shutil.move(orignal_path,location)
    return  f"Moved {orignal_path} to {location}."
@needle.tool
def remove_file(file_path:str):
    """Removes a file from the given path"""
    os.remove(file_path)
    return f"Removed file from path {file_path}"
@needle.tool
def copy_file(path:str,location:str):
    """Copies a file from one path to another"""
    shutil.copy2(path,location)
    return f"File copied from path {path} to {location}"
@needle.tool
def get_weather(location:str):
    """Get the current weather for a location, including temperature and wind speed."""
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

agent=needle.Needle(tools=[create_file,get_weather,web_search_wikipedia,read_file,open_file,move_file,remove_file,copy_file])
ai_response = agent.run(a)
print(ai_response["results"])
