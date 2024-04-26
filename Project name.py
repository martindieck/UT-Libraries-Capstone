import pandas as pd
import re
import sys

def split_project_name(project_name):
    if pd.isna(project_name):
        return None, None, None, 1  # Return 1 as the flag if the project name is NaN

    # Special case handling for "St." with specific formatting
    st_pattern = r'^St\.\s+\w+.*\.$'
    if re.match(st_pattern, project_name):
        return project_name.strip(), None, None, 0  # Pattern matches, so flag is 0

    # Regular expression pattern for splitting
    pattern = r'^(.*?)(\.)(?:(?!(?:St\.?\s+\w+(?:\s+\w+)*))(.*)(\b(?i:School|Branch|dormitory|Building|housing|office|center|parking|gym|bank|hotel|auditorium|dorms|room|gymnasium|pool|store|street|floor|buildings|porch|hall|ward|cottage|station|library|lobby|storefront|warehouse|tower|fireplace|dormitories|church|cafeteria|memorial|garage|gallery|mueseum|club|theater|park|house|entrance|chapel|lodge|lake|restaurant|shop|apartments|lounge|lab|plant|plot|wing|elevator|palace|temple|mall|garden|showroom|pharmacy|hospital|campus|laboratory|field|quarters|ground|residence|hill|Pavillion|mill|stadium|block|observatory|department|avenue|courts)\b.*?)(\.)|(?:(St\.?\s+\w+(?:\s+\w+)*))(.*))(.*$)'
    match = re.match(pattern, project_name)

    if match:
        if match.group(3) is not None:
            part1 = match.group(1).strip() + match.group(2) + match.group(3).strip() + match.group(4) + match.group(5)
            part2 = match.group(3).strip() + match.group(4)
        else:
            part1 = match.group(1).strip() + (match.group(6) if match.group(6) is not None else '') + (match.group(7) if match.group(7) is not None else '')
            part2 = match.group(7) if match.group(7) is not None else None
        part3 = match.group(1).strip()
        return part1, part2, part3, 0
    else:
        first_period_index = project_name.find('.')
        if first_period_index != -1:
            return project_name[:first_period_index], None, None, 1
        else:
            return None, None, None, 1

if len(sys.argv) != 3:
    print("Usage: python script.py <input_csv> <output_csv>")
    print("Number of arguments:", len(sys.argv))
    print("Argument List:", str(sys.argv))
    sys.exit(1)

# Input and output file paths
input_csv = sys.argv[1]
output_csv = sys.argv[2]

# Read the CSV file
df = pd.read_csv(input_csv, low_memory=False)

# Apply the function and create the columns
df[['Place name[1]', 'Place name[2]', 'Place name[3]', 'project_name_flag']] = pd.DataFrame(df['Project name'].apply(split_project_name).tolist(), index=df.index)

# Modify the flag for clean entries
df.loc[(~df['Place name[2]'].notnull()) & (~df['Place name[3]'].notnull()) & df['Place name[1]'].notnull(), 'project_name_flag'] = 0

# Include the 'Unique ID' and reorder the columns to include the new ones as desired
df = df[['unique ID', 'Project name', 'Place name[1]', 'Place name[2]', 'Place name[3]', 'project_name_flag']]

# Save the modified DataFrame back to a CSV file
df.to_csv(output_csv, index=False)

# Print the DataFrame with the new columns
print(df)
