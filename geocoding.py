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
    print(url)
    response = requests.get(url)

    if response.status_code == 200:
        print("GET request successful")
        print("Response body:")
        print(response.text)
    else:
        print(f"GET request failed with status code {response.status_code}")

address = ""
geocode(address)