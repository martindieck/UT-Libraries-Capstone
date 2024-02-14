import configparser
import requests
from urllib.parse import quote

def geocode_to_url(address, country_code):
    config = configparser.ConfigParser()
    config.read('config.ini')

    # API connection parameters
    api_key = config.get('geocoding', 'API_KEY')
    encoded_address = quote(address)
    url = f"https://api.geoapify.com/v1/geocode/search?text={encoded_address}&filter=countrycode:{country_code}&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        long = data["features"][0]["geometry"]["coordinates"][0]
        lat = data["features"][0]["geometry"]["coordinates"][1]
        print(f"https://maps.google.com/?q={lat},{long}")
    else:
        print(f"GET request failed with status code {response.status_code}")

def geocode_to_coords(address, country_code):
    config = configparser.ConfigParser()
    config.read('config.ini')

    # API connection parameters
    api_key = config.get('geocoding', 'API_KEY')
    encoded_address = quote(address)
    url = f"https://api.geoapify.com/v1/geocode/search?text={encoded_address}&filter=countrycode:{country_code}&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        long = data["features"][0]["geometry"]["coordinates"][0]
        lat = data["features"][0]["geometry"]["coordinates"][1]
        return lat, long
    else:
        print(f"GET request failed with status code {response.status_code}")

def geocode_complete(address, country_code):
    config = configparser.ConfigParser()
    config.read('config.ini')

    # API connection parameters
    api_key = config.get('geocoding', 'API_KEY')
    encoded_address = quote(address)
    url = f"https://api.geoapify.com/v1/geocode/search?text={encoded_address}&filter=countrycode:{country_code}&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        long = data["features"][0]["geometry"]["coordinates"][0]
        lat = data["features"][0]["geometry"]["coordinates"][1]
        link = f"https://maps.google.com/?q={lat},{long}"
        return lat, long, link
    else:
        print(f"GET request failed with status code {response.status_code}")

#geocode_to_url("", "none")