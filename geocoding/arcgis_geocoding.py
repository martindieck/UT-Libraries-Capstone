from arcgis.geocoding import geocode
from arcgis.gis import GIS
import configparser
import json # Used for debug process


def geocode_complete(address):
    """Function to geocode a lookup address using the ArcGIS API.
    Input: A lookup address as a string.
    Returns four values: generated_address, latitude, longitude, flag"""

    # Using configparser to read and process a personalized config.ini file that contains individual API information (See example_config.ini for more information)
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('geocoding', 'ARCGIS_API_KEY')

    #Initializing the ArcGIS Client and calling the geocoding function
    gis = GIS(api_key=api_key)
    geocode_result = geocode(address)

    # json_str = json.dumps(geocode_result, indent=4)           # Uncomment to analyze detailed JSON results from API for debugging process
    # print(json_str)

    # Try and Except blocks to obtain the specified results from the final JSON output
    try:
        generated_address = geocode_result[0]["address"]
    except:
        generated_address = ""
    try:
        lat = geocode_result[0]["location"]["y"]
    except:
        lat = ""
    try:
        lng = geocode_result[0]["location"]["x"]
    except:
        lng = ""
    try:
        flag = 1 if geocode_result[0]["score"] < 85 else 0
    except:
        flag = 1

    return generated_address, lat, lng, flag