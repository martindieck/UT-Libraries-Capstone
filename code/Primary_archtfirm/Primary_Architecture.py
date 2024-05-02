import pandas as pd
import re
import sys

def clean_name(name):
    """
    Clean the name by removing unwanted characters and dates.
    """
    name = re.sub('[^\x00-\x7F]+', '', name)  # Remove non-ASCII characters
    name = re.sub('\(\d{4}-\d{4}\)|\(\d{4}\)', '', name)  # Remove dates
    return name.strip()

def process_entry_v5(entry):
    """
    Process each entry with enhanced rules for corporate identification and name cleaning.
    Converts any non-string input into a string to handle NaN values.
    Returns both processed entries and a flag indicating processing status.
    """
    entry = str(entry)
    flag = 0  # Default flag, 0 means no issues

    if 'unidentified' in entry.lower():
        return [("", "", "")], 0  # Return empty values with flag set if problematic

    corporate_keywords = [
        'Group', 'Company', 'Corporation', 'Incorporated', 'Inc.', 'LLC', 'Ltd.',
        'and', '&', 'Architects', 'Architecture', 'Studio', 'Associates', 'Bureau',
        'Office of Supervising Architect', 'Engineering', 'Construction', 'Consultants',
        'Design', 'Partnership', 'Firm', 'PLLC', 'Office of',
        'Skidmore Owings Merrill', 'Venturi Rauch & Scott Brown', 'architectural firm',
        'architects', 'architecture', 'engineering', 'construction', 'design studio'
    ]

    entry = clean_name(entry)
    primary_entities = [e.strip() for e in entry.split(';')]
    processed_entries = []

    for entity in primary_entities:
        if '|' in entity:
            name, role = [part.strip() for part in entity.split('|', 1)]
        else:
            name, role = entity, 'contributor'
        
        entity_type = 'corporate' if any(keyword.lower() in name.lower() for keyword in corporate_keywords) else 'person'
        processed_entries.append((name, role, entity_type))
    
    return processed_entries, flag

def expand_entries(row):
    """
    Expand processed entries into separate columns within the same row.
    Includes processing flag.
    """
    expanded_data = {}
    entries, flag = row['Processed']
    for i, (name, role, entity_type) in enumerate(entries, start=1):
        expanded_data[f'Primary archt/firm[{i}][Name]'] = name
        expanded_data[f'Primary archt/firm[{i}][Role]'] = role
        expanded_data[f'Primary archt/firm[{i}][Type]'] = entity_type
    expanded_data['Primary archt/firm_flag'] = flag
    return pd.Series(expanded_data)

def process_and_save_csv(input_csv_path, output_csv_path):
    """
    Load the input CSV, process it with the latest rules, and save the outputs.
    """
    df = pd.read_csv(input_csv_path)
    
    df['Processed'] = df['Primary archt/firm'].apply(process_entry_v5)
    expanded_df = df.apply(expand_entries, axis=1)
    
    # Concatenate the original dataframe with the expanded dataframe
    result_df = pd.concat([df, expanded_df], axis=1)
    
    # Drop the 'Processed' column which is no longer needed
    result_df = result_df.drop(columns=['Processed'])

    # Select only the desired columns
    desired_columns = ['unique ID', 'Primary archt/firm'] + \
                      [col for col in result_df.columns if 'Primary archt/firm[' in col] + \
                      ['Primary archt/firm_flag']
    result_df = result_df[desired_columns]
    
    # Save the result to a CSV file
    result_df.to_csv(output_csv_path, index=False)
    print(f"All data saved to {output_csv_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python Primary_Architecture.py <input_csv_path> <output_csv_path>")
        sys.exit(1)
    
    input_csv_path = sys.argv[1]
    output_csv_path = sys.argv[2]
    process_and_save_csv(input_csv_path, output_csv_path)
