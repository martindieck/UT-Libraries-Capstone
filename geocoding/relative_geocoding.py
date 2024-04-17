import pandas as pd
import csv
from tqdm import tqdm
from google_geocoding import geocode_complete # Change From to use different geocoding modules (ArcGIS, Google Maps, GeoApify)

field_names = ["ID", "Lookup", "City", "State", "County", "Country", "Latitude", "Longitude", "Flag"]
geocoded_locations = []
id = 1

df = pd.read_csv('collections.csv')
df = df.fillna('')
unique_combinations = df.groupby(['City', 'State/Province', 'County', 'Country']).size().reset_index().rename(columns={0:'count'}).sort_values(by='count', ascending=False)

for index, row in tqdm(unique_combinations.iterrows(), total=len(unique_combinations)):
    row_dict = {}
    unique_id = id
    city = row["City"]
    state = row["State/Province"]
    county = row["County"]
    country = row["Country"]
    lookup = city + state + county + country
    if city == "" and state == "" and county == "" and country == "":
        latitude = ""
        longitude = ""
        flag = 0
    else:
        address_list = [city, county, state, country]
        address = [i for i in address_list if i != ""]
        address = ", ".join(address_list)
        normal_address, latitude, longitude, flag = geocode_complete(address)
    row_dict["ID"] = unique_id
    row_dict["Lookup"] = lookup
    row_dict["City"] = city
    row_dict["State"] = state
    row_dict["County"] = county
    row_dict["Country"] = country
    row_dict["Latitude"] = latitude
    row_dict["Longitude"] = longitude
    row_dict["Flag"] = flag
    geocoded_locations.append(row_dict)
    id += 1

with open('geocoded_locations.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(geocoded_locations)