import pandas as pd
import numpy as np
import csv
from tqdm import tqdm
from countrycode import get_country_code
from geocoding import geocode_complete
from get_collection import get_collection

collection_code = "DAHL"

field_names = ["ID", "Project", "Latitude", "Longitude", "Link"]
geocoded_collection = []

collection_df = get_collection(collection_code)

for index, row in tqdm(collection_df.iterrows(), total=len(collection_df)):
    row_dict = {}
    unique_id = row["unique ID"]
    project_name = row["Project name"]
    country_code = get_country_code(row["Country"])
    if row["Street address"] == "" and row["City"] == "" and row["State/Province"] == "" and row["Country"] == "":
        latitude = ""
        longitude = ""
        link = ""
    else:
        address_list = [row["Project name"], row["Street address"], row["City"], row["County"], row["State/Province"], row["Country"]]
        address = ", ".join(address_list)
        latitude, longitude, link = geocode_complete(address, country_code)
    row_dict["ID"] = unique_id
    row_dict["Project"] = project_name
    row_dict["Latitude"] = latitude
    row_dict["Longitude"] = longitude
    row_dict["Link"] = link
    geocoded_collection.append(row_dict)

with open(collection_code + '.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(geocoded_collection)