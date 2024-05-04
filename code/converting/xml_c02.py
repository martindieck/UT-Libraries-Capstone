from xml.etree.ElementTree import Element
import xml_c03
from xml_utils import safe_str, add_elements


def process_entities(c02, row, entity_type, role='Client'):
    """Processes entities (Primary architects/firms, Collaborators, Clients) and appends them to the c02 element.

    Parameters:
    - c02: The parent XML element to which the entities will be appended.
    - row: The data row containing entity information.
    - entity_type: The type of entity to process, e.g., 'Primary archt/firm', 'Collaborator', 'Client'.
    - role: The role attribute for the entity (default is 'Client').
    """
    i = 1
    while True:
        name_key = f'{entity_type}[{i}][Name]'
        name_value = safe_str(row.get(name_key))
        if not name_value:
            break

        origination = Element('origination')
        c02.append(origination)

        role_value = safe_str(row.get(f'{entity_type}[{i}][Role]', role))
        type_value = safe_str(row.get(f'{entity_type}[{i}][Type]'))
        element_tag = 'persname' if type_value.lower() == 'person' else 'corpname'

        entity_info = [{
            'text': name_value,
            'attrib': {'role': role_value},
            'tag': element_tag,

        }]
        # Using add_elements to streamline element addition
        add_elements(origination, element_tag, entity_info)

        i += 1


def add_control_access_and_notes(c02, row):
    """
    Adds 'controlaccess' and 'note' elements to the 'c02' element based on data from 'row'.

    The 'controlaccess' element is populated with geographic names and attributes sourced from the row.
    The 'note' elements are populated with various fields such as city, country, and notes.

    Parameters:
    - c02 (Element): The parent XML Element to which the 'controlaccess' and 'note' will be added.
    - row (dict): A dictionary representing the data row, with expected keys for geographic and note information.
    """

    controlaccess = Element('controlaccess')
    c02.append(controlaccess)

    controlaccess_geogname_info = [
        {'text': safe_str(row.get('FAST Geographic', '')),
         'attrib': {'source': 'fast'}},
        # {'text': row.get('Place name', ''), 'attrib': {'source': 'local'}}
    ]

    # Extract 'Place name' information with dynamic keys
    i = 1
    while True:
        place_name_key = f'Place name[{i}]'
        place_name_value = safe_str(row.get(place_name_key))
        if not place_name_value:
            break
        controlaccess_geogname_info.append(
            {'text': place_name_value, 'attrib': {'source': 'local'}})
        i += 1

    # Define controlaccess types and extract corresponding values for geoform tag
    controlaccess_genreform_info = []
    # Define controlaccess types and extract corresponding values
    controlaccess_types = [
        'Material types[standard]', 'Set type', 'Media']

    # Set to track entries for specified controlaccess types to avoid duplicates
    seen_types = set()
    for key_base in controlaccess_types:
        i = 1
        while True:
            key = f'{key_base}[{i}]'
            value = safe_str(row.get(key))
            if not value:
                break

            key_src = f'{key_base}_src[{i}]'
            attr = {'source': safe_str(row.get(key_src))}
            # attr = {'source': 'aat' if key_base != 'Media' else 'gmgpc'}
            # Create a unique key based on value and source
            unique_key = (value, attr['source'])
            if unique_key not in seen_types:
                seen_types.add(unique_key)
                controlaccess_genreform_info.append(
                    {'text': value, 'attrib': attr})
            i += 1

    add_elements(controlaccess, 'geogname', controlaccess_geogname_info)
    add_elements(controlaccess, 'genreform', controlaccess_genreform_info)

    # Define note fields and append note elements to 'c02'
    notes_fields = ['City', 'County', 'State/Province', 'Country', 'Street address',
                    'Street address (normalized)', 'Coordinates (normalized)', 'Coordinates (relative)', 'Project number', 'Number of items',
                    'Notes', 'Accession #', 'Processor', 'Processing completion date', 'Entry_date_normalized',
                    'Rev_date_normalized']
    for field in notes_fields:
        note = Element('note')
        c02.append(note)
        note_text = f"{field}: {safe_str(row.get(field, 'N/A'))}"
        add_elements(note, 'p', [{'text': note_text}])

    # Manage 'unique ID' separately due to its special prefix.
    note = Element('note')
    c02.append(note)
    note_text = f"AAA Projects Database Unique ID: {safe_str(row.get('unique ID', 'N/A'))}"
    add_elements(note, 'p', [{'text': note_text}])


def create_c02(row):
    """Creates a c02 XML element for a single row of data.

    Parameters:
    - row: The data row from which the XML element will be generated.

    Returns:
    - An ElementTree Element representing the c02 element.
    """
    c02 = Element('c02', level="otherlevel", otherlevel="Project")
    did = Element('did')
    c02.append(did)
    add_elements(did, 'unittitle', [
        {'text': safe_str(row.get('Project name', ''))}
    ])
    add_elements(did, 'unitdate', [
        {'text': safe_str(
            row.get('Date normalized'))}
    ])
    # Process primary architects/firms, collaborators, and clients
    entities_fields = ['Primary archt/firm', 'Collaborator', 'Client']
    for field in entities_fields:
        process_entities(c02, row, field)

    add_control_access_and_notes(c02, row)

    # Assuming c03.create_c03_for_materials function exists and is correctly implemented
    c03_elements = xml_c03.create_c03_for_materials(row)
    for element in c03_elements:
        c02.append(element)

    return c02

# Example usage:
# row_data = {
#     'Project name': 'Sample Project',
#     'Date normalized': '2022',
#     # Add other fields as necessary
# }
# xml_element = create_c02(row_data)
# print(parseString(tostring(xml_element)).toprettyxml())
