import sys
import pandas as pd
import re

# Define the functions for processing


def extract_role(name_role):
    if '|' in name_role:
        name, role = map(str.strip, name_role.split('|', 1))
    else:
        name, role = name_role.strip(), 'Contributor'  # Default role assignment
    return name, role


def infer_type_and_flag(name):
    company_indicators = [
        "inc", "llc", "ltd", "group", "firm", "studio", "associates", "corporation",
        "company", "systems", "technologies", "solutions"
    ]
    ambiguous_indicators = ["and", "&"]
    person_indicators = ["dr.", "ph.d"]

    name_lower = name.lower()
    if any(indicator in name_lower for indicator in company_indicators):
        return 'company', 0
    elif any(indicator in name_lower for indicator in ambiguous_indicators):
        if " and " in name_lower or " & " in name_lower:
            return 'company', 1  # Flagged as it could be interpreted in multiple ways
        else:
            return 'company', 0
    elif any(title in name_lower for title in person_indicators):
        return 'person', 0
    else:
        # Default to person, but flag as ambiguous due to lack of clear indicators
        return 'person', 1


def process_collaborators(collaborators):
    if pd.isna(collaborators):
        return []
    collaborator_list = collaborators.split(';')
    structured_data = []
    for collaborator in collaborator_list:
        name, role = extract_role(collaborator)
        name = re.sub(r'\.$', '', name)  # Remove trailing period if present
        collaborator_type, flag = infer_type_and_flag(name)
        structured_data.append({
            "Name": name,
            "Type": collaborator_type,
            "Role": role,
            "Flag": flag
        })
    return structured_data


# Check if correct number of command-line arguments are provided
if len(sys.argv) != 3:
    print("Usage: python Collaborator.py <input csv> <output csv>")
    sys.exit(1)

input_filename = sys.argv[1]
output_filename = sys.argv[2]

# Load the Excel file
data = pd.read_csv(input_filename)

# Apply the processing function to the "Collaborators:" column
data['Structured Collaborators'] = data['Collaborators:'].apply(
    process_collaborators)

# Determine the maximum number of collaborators
max_collaborators = data['Structured Collaborators'].apply(len).max()

# Add new columns to the original dataframe for each collaborator's details
for i in range(max_collaborators):
    data[f'Collaborators[{i+1}][Name]'] = data['Structured Collaborators'].apply(
        lambda x: x[i]['Name'] if i < len(x) else None)
    data[f'Collaborators[{i+1}][Type]'] = data['Structured Collaborators'].apply(
        lambda x: x[i]['Type'] if i < len(x) else None)
    data[f'Collaborators[{i+1}][Role]'] = data['Structured Collaborators'].apply(
        lambda x: x[i]['Role'] if i < len(x) else None)
    data[f'Collaborators[{i+1}]_flag'] = data['Structured Collaborators'].apply(
        lambda x: x[i]['Flag'] if i < len(x) else None)

# Remove the now unnecessary 'Structured Collaborators' column
data = data.drop(columns=['Structured Collaborators'])

# Save the transformed data to a new Excel file
data.to_csv(output_filename, index=False)

print(f"Data has been processed and saved to '{output_filename}'.")
