import pandas as pd

def get_relative_coords(lookup_value, csv_file):
    """Function to obtain the relative coordinates for a specific "city-county-state-country" lookup value.
    Inputs: lookup value as a string (Ex. AustinTravisTexasUnited States), a csv_file containing the final relative geocoding values (see relative_geocoding.py)
    Returns: relative_latitude, relative_longitude, relative_flag
    """
    df = pd.read_csv(csv_file)

    result = df[df.iloc[:, 1] == lookup_value] # Return the whole row with specified lookup value
    if len(result) == 0:
        return None  # If lookup_value not found, return None
    
    # Extract Latitude, Longitude, and Flag columns
    relative_latitude = result.iloc[0]['Latitude']
    relative_longitude = result.iloc[0]['Longitude']
    relative_flag = result.iloc[0]['Flag']

    return relative_latitude, relative_longitude, relative_flag
