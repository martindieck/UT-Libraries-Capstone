import pandas as pd

def get_relative_coords(lookup_value, csv_file):
    df = pd.read_csv(csv_file)

    result = df[df.iloc[:, 1] == lookup_value]
    if len(result) == 0:
        return None  # If lookup_value not found, return None
    
    # Extract Latitude, Longitude, and Link columns
    latitude = result.iloc[0]['Latitude']
    longitude = result.iloc[0]['Longitude']
    link = result.iloc[0]['Link']

    return latitude, longitude, link
