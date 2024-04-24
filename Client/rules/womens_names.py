import json
import pandas as pd

# Specify the path to your Excel sheet
file_path = "../womens_names.xlsx"

# Read the specific sheet using pandas.read_excel
df = pd.read_excel(file_path, usecols=['Client', 'client1', 'client2'])

# Setting the index to 'Client' for easier manipulation
df.set_index('Client', inplace=True)

# Function to create a dictionary where each value is "person"
def make_person_dict(row):
    return {name.strip(): "person" for name in row if pd.notna(name)}

# Applying the function to each row in the DataFrame
json_output = df.apply(make_person_dict, axis=1).to_dict()

# Printing the JSON output
print(json_output)


# File path for the JSON file
json_file_path = 'womens_names.json'

# Writing the dictionary to a JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(json_output, json_file)

print(f'JSON saved to {json_file_path}')