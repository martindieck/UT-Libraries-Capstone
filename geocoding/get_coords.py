import pandas as pd
import numpy as np
import csv
from tqdm import tqdm
from countrycode import get_country_code
from google_geocoding import geocode_complete # Change From to use different geocoding modules (ArcGIS, Google Maps, GeoApify)
from get_collection import get_collection
from get_relative_coords import get_relative_coords

collection_code = "FG"

field_names = [
    "ID",
    "Project",
    "Original_Address",
    "City",
    "State",
    "County",
    "Country",
    "Relative_Latitude",
    "Relative_Longitude",
    "Relative_Link",
    "Generated_Address",
    "Exact_Latitude",
    "Exact_Longitude",
    "Exact_Link",
    "Validation",
    "Notes"
]
geocoded_collection = []

collection_df = get_collection(collection_code)
collection_df = collection_df.fillna('')

for index, row in tqdm(collection_df.iterrows(), total=len(collection_df)):
    #Initial Parameter Definition
    row_dict = {}
    unique_id = row["unique ID"]
    project_name = row["Project name"]
    original_address = row["Street address"]
    city = row["City"]
    state = row["State/Province"]
    county = row["County"]
    country = row["Country"]
    lookup_value = city + state + county + country
    #country_code = get_country_code(row["Country"])                # Turn on if using GeoApify for more accurate results

    # Obtaining Relative Geocode Values
    relative_latitude, relative_longitude, relative_link = get_relative_coords(lookup_value, "geocoded_locations.csv")

    # Initiating Geocoding process if there is any information at all
    if original_address == "" and city == "" and state == "" and county == "" and country == "":
        exact_latitude = ""
        exact_longitude = ""
        link = ""
    else:
        address_list = [project_name, original_address, city, county, state, country]
        address = [i for i in address_list if i != ""]
        address = ", ".join(address_list)
        generated_address, exact_latitude, exact_longitude, exact_link = geocode_complete(address)

    #Setting Final CSV Fields
    row_dict["ID"] = unique_id
    row_dict["Project"] = project_name
    row_dict["Original_Address"] = original_address
    row_dict["City"] = city
    row_dict["State"] = state
    row_dict["County"] = county
    row_dict["Country"] = country
    row_dict["Relative_Latitude"] = relative_latitude
    row_dict["Relative_Longitude"] = relative_longitude
    row_dict["Relative_Link"] = relative_link
    row_dict["Generated_Address"] = generated_address
    row_dict["Exact_Latitude"] = exact_latitude
    row_dict["Exact_Longitude"] = exact_longitude
    row_dict["Exact_Link"] = exact_link
    row_dict["Validation"] = ""
    row_dict["Notes"] = ""
    geocoded_collection.append(row_dict)

with open(collection_code + '.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(geocoded_collection)