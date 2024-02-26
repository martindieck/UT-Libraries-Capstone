import pandas as pd
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import xml_c02
import os
from datetime import datetime


def create_full_xml_from_row(df):
    """
    Creates a full XML document from a DataFrame, where each row represents a project.

    Parameters:
    - df: A pandas DataFrame containing project data.

    Returns:
    - A pretty-printed XML string representing the entire collection of projects.
    """
    # Root element of the XML document
    ead = Element('ead')
    archdesc = SubElement(
        ead, 'archdesc', level="collection", type="inventory")
    dsc = SubElement(archdesc, 'dsc')
    c01 = SubElement(dsc, 'c01', level="series")

    # Set the title for the series
    did = SubElement(c01, 'did')
    SubElement(did, 'unittitle').text = 'Projects'

    # Process each row in the DataFrame to create c02 elements
    for index, row in df.iterrows():
        print(
            f"Processing row: {index + 1}, Project ID: {row.get('unique ID', 'N/A')}")
        c02_element = xml_c02.create_c02(row)
        if c02_element is not None:
            c01.append(c02_element)
        else:
            print("Encountered an issue with creating c02 element. Skipping.")

        # Check for an empty 'unique ID' indicating potential end of useful data
        if pd.isna(row['unique ID']):
            print("Detected an empty 'unique ID', stopping processing.")
            break

    # Convert the EAD element tree to a string and format it for readability
    xml_str = tostring(ead, 'utf-8')
    pretty_xml_str = parseString(xml_str).toprettyxml(indent="  ")

    return pretty_xml_str


def save_xml_to_file(xml_str, folder_path):
    """
    Saves an XML string to a file within a specified folder, appending a timestamp to the filename to prevent overwrites.

    Parameters:
    - xml_str: The XML string to save.
    - folder_path: The folder path where the XML file should be saved.
    """
    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)

    # Format the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_path = os.path.join(folder_path, f"output_{timestamp}.xml")

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(xml_str)

    return file_path


# Load the spreadsheet
spreadsheet_path = './converting/AAA-Proj-db-20231222-xlsx (matched_xml_template).xlsx'
df = pd.read_excel(spreadsheet_path)

# Generate XML using the create_full_xml_from_row function
example_xml = create_full_xml_from_row(df)

# Specify the folder path for the output file
output_folder_path = './output_xmls'

# Save the XML to the specified folder
output_file_path = save_xml_to_file(example_xml, output_folder_path)

print(f"XML has been saved to {output_file_path}")
