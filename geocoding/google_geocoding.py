import googlemaps
import configparser

def geocode_complete(address):
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('geocoding', 'GOOGLE_API_KEY')

    gmaps = googlemaps.Client(key=api_key)
    geocode_result = gmaps.geocode(address)
    #print(geocode_result)

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
        link = f"https://maps.google.com/?q={lat},{lng}"
    except:
        link = ""
    #print(address)
    #print(link)
    return normal_address, lat, lng, link

normal_address, lat, lng, link = geocode_complete("Cuauhtemoc")

print(link)