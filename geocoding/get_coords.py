import pandas as pd
import numpy as np
import csv
from tqdm import tqdm
from countrycode import get_country_code
from google_geocoding import geocode_complete # Change From to use different geocoding modules (ArcGIS, Google Maps, GeoApify)
from get_collection import get_collection

collection_code = "FG"

field_names = ["ID", "Project", "Normal Address", "Latitude", "Longitude", "Link"]
geocoded_collection = []

collection_df = get_collection(collection_code)

for index, row in tqdm(collection_df.iterrows(), total=len(collection_df)):
    row_dict = {}
    unique_id = row["unique ID"]
    project_name = row["Project name"]
    #country_code = get_country_code(row["Country"])                # Turn on if using GeoApify for more accurate results
    if row["Street address"] == "" and row["City"] == "" and row["State/Province"] == "" and row["Country"] == "":
        latitude = ""
        longitude = ""
        link = ""
    else:
        address_list = [row["Project name"], row["Street address"], row["City"], row["County"], row["State/Province"], row["Country"]]
        address = [i for i in address_list if i != ""]
        address = ", ".join(address_list)
        normal_address, latitude, longitude, link = geocode_complete(address)
    row_dict["ID"] = unique_id
    row_dict["Project"] = project_name
    row_dict["Normal Address"] = normal_address
    row_dict["Latitude"] = latitude
    row_dict["Longitude"] = longitude
    row_dict["Link"] = link
    geocoded_collection.append(row_dict)

with open(collection_code + '.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(geocoded_collection)