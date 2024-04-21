import googlemaps
import configparser
import json

def geocode_complete(address):
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('geocoding', 'GOOGLE_API_KEY')

    gmaps = googlemaps.Client(key=api_key)
    geocode_result = gmaps.geocode(address)

    # json_str = json.dumps(geocode_result, indent=4)
    # print(json_str)

    try:
        normal_address = geocode_result[0]["formatted_address"]
    except:
        normal_address = ""
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
        flag = 0

    return normal_address, lat, lng, flag

# normal_address, lat, lng, flag = geocode_complete("Bastrop, Bastrop, Texas, United States")
# print(flag)