import needle
import requests
from urllib.parse import quote
a=input("What do you want to do?: ")
@needle.tool
def create_file(file_name:str,value:str):
    """Create a file and with a value"""
    with open(file_name,"w") as f:
        f.write(value)
    return{
        "Output":f"Created a file {file_name}"
    }
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
    return{
        "output":f"its {temp}°C in {location} right now , with a wind speed of about {wind}km/h"
    }
@needle.tool
def web_search_wikipedia(qu:str):
    """Searches for an object . DO THIS ONLY FOR NAMES , PLACES , ITEM"""
    headers = {
        "User-Agent": "Jarvis/1.0 (https://github.com/gggff123/J-bot)",
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

    return {
        "extract": article,
    }

agent=needle.Needle(tools=[create_file,get_weather,web_search_wikipedia])
print(agent.run(a))
