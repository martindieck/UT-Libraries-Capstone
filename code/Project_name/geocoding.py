import configparser
import requests
from urllib.parse import quote

def geocode(address):
    config = configparser.ConfigParser()
    config.read('config.ini')

    # API connection parameters
    api_key = config.get('geocoding', 'API_KEY')
    encoded_address = quote(address)
    url = f"https://api.geoapify.com/v1/geocode/search?text={encoded_address}&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        long = data["features"][0]["geometry"]["coordinates"][0]
        lat = data["features"][0]["geometry"]["coordinates"][1]
        print(f"https://maps.google.com/?q={lat},{long}")
    else:
        print(f"GET request failed with status code {response.status_code}")

address = ""
geocode(address)