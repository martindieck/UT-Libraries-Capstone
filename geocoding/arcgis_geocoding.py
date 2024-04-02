from arcgis.geocoding import geocode
from arcgis.gis import GIS
import configparser

def geocode_complete(address):
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('geocoding', 'ARCGIS_API_KEY')

    gis = GIS(api_key=api_key)

    geocode_result = geocode(address)
    print(geocode_result[0])

    # lat = geocode_result[0]["geometry"]["location"]["lat"]
    # lng = geocode_result[0]["geometry"]["location"]["lng"]
    # link = f"https://maps.google.com/?q={lat},{lng}"
    # print(address)
    # print(link)
    # return lat, lng, link

# lat, lng, link = geocode_complete("University of Texas.  Engineering Building")

geocode_complete("McCombs School of Business, austin texas")

# print(link)