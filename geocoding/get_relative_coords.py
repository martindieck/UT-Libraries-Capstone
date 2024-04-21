import pandas as pd

def get_relative_coords(lookup_value, csv_file):
    df = pd.read_csv(csv_file)

    result = df[df.iloc[:, 1] == lookup_value]
    if len(result) == 0:
        return None  # If lookup_value not found, return None
    
    # Extract Latitude, Longitude, and Flag columns
    latitude = result.iloc[0]['Latitude']
    longitude = result.iloc[0]['Longitude']
    flag = result.iloc[0]['Flag']

    return latitude, longitude, flag
