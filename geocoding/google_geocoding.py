import googlemaps
import configparser
import json # Used for debug process

def geocode_complete(address, api_key_external):
    """Function to geocode a lookup address using the Google Maps API.
    Input: A lookup address as a string.
    Returns four values: generated_address, latitude, longitude, flag"""

    # Using configparser to read and process a personalized config.ini file that contains individual API information (See example_config.ini for more information)
    # config = configparser.ConfigParser()
    # config.read('config.ini')
    # api_key = config.get('geocoding', 'GOOGLE_API_KEY')
    api_key = api_key_external

    #Initializing the Google Maps Client and calling the geocoding function
    gmaps = googlemaps.Client(key=api_key)
    geocode_result = gmaps.geocode(address)

    # json_str = json.dumps(geocode_result, indent=4)           # Uncomment to analyze detailed JSON results from API for debugging process
    # print(json_str)

    # Try and Except blocks to obtain the specified results from the final JSON output
    try:
        generated_address = geocode_result[0]["formatted_address"]
    except:
        generated_address = ""
    try:
        lat = geocode_result[0]["geometry"]["location"]["lat"]
    except:
        lat = ""
    try:
        lng = geocode_result[0]["geometry"]["location"]["lng"]
    except:
        lng = ""
    try:
        flag = int(geocode_result[0]["partial_match"] == True)
    except:
        flag = 1

    return generated_address, lat, lng, flag