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

    # Set the length threshold for name review
    length_threshold = 40

    company_indicators = [
        r"\binc\b", r"\bllc\b", r"\bltd\b", r"\bgroup\b", r"\bfirm\b", r"\bstudio\b",
        r"\bassociates\b", r"\bcorporation\b", r"\bcompany\b", r"\bsystems\b",
        r"\btechnologies\b", r"\bsolutions\b", r"\bco\.", r"\bcorp\.", r"\bcorp\b",
        r"\bengineering\b", r"\barchitectural\b", r"\barchitects\b", r"\barchitect\b",
        r"\bservices\b", r"\bassoc\.", r"\buniversity\b", r"\bengineers\b", r"\bengineer\b", r"\binvestments\b",
        r"\bconstruction\b", r"\band\b", r".*?&.*", r"\bfederal\b", r"u\.s\.\b", r"\bdepartment\b", r"\boffice\b",
        r"\bdesign\b"
    ]
    ambiguous_indicators = [r"\baustin\b", r"\bbrothers\b", r"/"]
    person_indicators = [r"\bdr\.\b", r"\bph\.d\b", r"\bASLA\b"]

    name_lower = name.lower()

    # Check if the length of the name exceeds the set threshold
    if len(name_lower) > length_threshold:
        # Mark for manual review due to excessive length
        return 'long name needs review', 1

    if any(re.search(indicator, name_lower) for indicator in company_indicators):
        return 'company', 0
    elif any(re.search(indicator, name_lower) for indicator in ambiguous_indicators):
        # Flagged as it could be interpreted in multiple ways
        return 'unsure needs review', 1

    elif any(re.search(title, name_lower) for title in person_indicators):
        return 'person', 0
    else:
        # Default to person, but flag as ambiguous due to lack of clear indicators
        return 'person', 0


def process_collaborators(collaborators):
    if pd.isna(collaborators):
        return []
    collaborator_list = collaborators.split(';')
    structured_data = []
    for collaborator in collaborator_list:
        name, role = extract_role(collaborator)
        collaborator_type, flag = infer_type_and_flag(name)
        if collaborator_type == 'person':
            # Remove trailing period for person name if present
            name = re.sub(r'\.$', '', name)
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

print(data.head())

# Apply the processing function to the "Collaborators:" column
data['Structured Collaborators'] = data['Collaborators:'].apply(
    process_collaborators)

# Determine the maximum number of collaborators
max_collaborators = data['Structured Collaborators'].apply(len).max()

# Add new columns to the original dataframe for each collaborator's details
for i in range(max_collaborators):
    data[f'Collaborator[{i+1}][Name]'] = data['Structured Collaborators'].apply(
        lambda x: x[i]['Name'] if i < len(x) else None)
    data[f'Collaborator[{i+1}][Type]'] = data['Structured Collaborators'].apply(
        lambda x: x[i]['Type'] if i < len(x) else None)
    data[f'Collaborator[{i+1}][Role]'] = data['Structured Collaborators'].apply(
        lambda x: x[i]['Role'] if i < len(x) else None)
    data[f'Collaborator[{i+1}]_flag'] = data['Structured Collaborators'].apply(
        lambda x: x[i]['Flag'] if i < len(x) else None)

# Selecting only specified columns
output_columns = ['unique ID', 'Collaborators:']
for i in range(max_collaborators):
    output_columns.extend([
        f'Collaborator[{i+1}][Name]',
        f'Collaborator[{i+1}][Type]',
        f'Collaborator[{i+1}][Role]',
        f'Collaborator[{i+1}]_flag'
    ])

final_output = data[output_columns]

# Save the transformed data to a new CSV file
final_output.to_csv(output_filename, index=False)

print(f"Data has been processed and saved to '{output_filename}'.")
