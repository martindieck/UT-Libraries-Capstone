import configparser
import requests # Using the requests library to call the API
from urllib.parse import quote  # Parsing the lookup address to include it in the API URL
import json # Used for debug process

def geocode_complete(address, country_code):
    """Function to geocode a lookup address using the GeoApify API.
    Input: A lookup address as a string, a two-letter country code. (address, country_code)
    Returns four values: generated_address, latitude, longitude, flag"""

    # Using configparser to read and process a personalized config.ini file that contains individual API information (See example_config.ini for more information)
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('geocoding', 'GEOAPIFY_API_KEY')
    
    # Parsing the lookup address to include it in the API URL
    encoded_address = quote(address)
    
    # Calling the API URL directly
    url = f"https://api.geoapify.com/v1/geocode/search?text={encoded_address}&bias=countrycode:{country_code}&apiKey={api_key}"
    response = requests.get(url)

    # Check if API call was successful
    if response.status_code == 200:
        geocode_result = response.json()
        
        # json_str = json.dumps(geocode_result, indent=4)           # Uncomment to analyze detailed JSON results from API for debugging process
        # print(json_str)
        
        # Try and Except blocks to obtain the specified results from the final JSON output
        try:
            generated_address = geocode_result["features"][0]["properties"]["formatted"]
        except:
            generated_address = ""
        try:
            lat = geocode_result["features"][0]["properties"]["lat"]
        except:
            lat = ""
        try:
            lng = geocode_result["features"][0]["properties"]["lon"]
        except:
            lng = ""
        try:
            flag = 1 if geocode_result["features"][0]["properties"]["rank"]["confidence"] < 0.8 else 0
        except:
            flag = 1
        return generated_address, lat, lng, flag
    else:
        print(f"GET request failed with status code {response.status_code}")
        return "", "", "", ""