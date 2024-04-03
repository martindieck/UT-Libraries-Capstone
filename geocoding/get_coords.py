import pandas as pd
import numpy as np
import csv
from tqdm import tqdm
from countrycode import get_country_code
from google_geocoding import geocode_complete # Change From to use different geocoding modules (ArcGIS, Google Maps, GeoApify)
from get_collection import get_collection

collection_code = "FG"

field_names = ["ID", "Project", "Address", "City", "State", "County", "Country", "Latitude", "Longitude", "Link", "Validation"]
geocoded_collection = []

collection_df = get_collection(collection_code)

for index, row in tqdm(collection_df.iterrows(), total=len(collection_df)):
    row_dict = {}
    unique_id = row["unique ID"]
    project_name = row["Project name"]
    city = row["City"]
    state = row["State/Province"]
    county = row["County"]
    country = row["Country"]
    #country_code = get_country_code(row["Country"])                # Turn on if using GeoApify for more accurate results
    if row["Street address"] == "" and city == "" and state == "" and county == "" and country == "":
        latitude = ""
        longitude = ""
        link = ""
    else:
        address_list = [project_name, row["Street address"], city, county, state, country]
        address = [i for i in address_list if i != ""]
        address = ", ".join(address_list)
        normal_address, latitude, longitude, link = geocode_complete(address)
    row_dict["ID"] = unique_id
    row_dict["Project"] = project_name
    row_dict["Address"] = normal_address
    row_dict["City"] = city
    row_dict["State"] = state
    row_dict["County"] = county
    row_dict["Country"] = country
    row_dict["Latitude"] = latitude
    row_dict["Longitude"] = longitude
    row_dict["Link"] = link
    row_dict["Validation"] = ""
    geocoded_collection.append(row_dict)

with open(collection_code + '.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(geocoded_collection)