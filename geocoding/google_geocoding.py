import googlemaps
import configparser

def geocode_complete(address):
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('geocoding', 'API_KEY')

    gmaps = googlemaps.Client(key=api_key)
    geocode_result = gmaps.geocode(address)

    lat = geocode_result[0]["geometry"]["location"]["lat"]
    lng = geocode_result[0]["geometry"]["location"]["lng"]
    link = f"https://maps.google.com/?q={lat},{lng}"
    # print(address)
    # print(link)
    return lat, lng, link

# lat, lng, link = geocode_complete("University of Texas.  Engineering Building")

# print(link)