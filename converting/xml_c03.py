import pandas as pd
from xml.etree.ElementTree import Element
from xml_utils import safe_str, add_elements


def create_c03_for_materials(row):
    """
    Generates a list of c03 XML elements for materials specified in a row.

    Parameters:
    - row: A pandas Series or dict-like object representing a row of data.

    Returns:
    - A list of ElementTree Element objects, each representing a c03 element.
    """

    c03_elements = []
    m = 1  # Start index for material types

    while True:
        material_key = f'Material types[original][{m}]'
        material_value = safe_str(row.get(material_key))

        if not material_value:
            break

        c03 = Element('c03', attrib={'level': 'file'})

        did = Element('did')
        c03.append(did)

        # Setting 'unittitle' and 'unitdate' using add_elements
        add_elements(did, 'unittitle', [{'text': material_value}])
        add_elements(did, 'unitdate', [
                     {'text': safe_str(row.get('Date normalized'))}])

        # Additional processing based on material type, e.g., 'drawings'
        if material_value.lower() == 'drawings':
            process_drawings_material(c03, row)

        c03_elements.append(c03)
        m += 1  # Proceed to next material

    return c03_elements


def process_drawings_material(c03, row):
    """
    Processes and adds specific elements to a c03 element for 'drawings' material.

    Parameters:
    - c03: The c03 XML element being processed.
    - row: The row data from which to extract information.
    """

    # Container elements
    container_types = ['box', 'folder', 'roll']

    # Add container elements
    add_container_elements(c03, row, container_types)

    # Adding notes fields specific to 'drawings'
    notes_fields = [
        'Date on drawings', 'Pres. notes:', 'treatment completed A',
        'treatment completed B', 'treatment completed C',
        'treatment completed D', 'treatment completed E'
    ]
    add_notes_fields(c03, row, notes_fields)


def add_notes_fields(c03, row, fields):
    """
    Adds note elements for specified fields if they have values.

    Parameters:
    - c03: The c03 XML element being processed.
    - row: The row data from which to extract information.
    - fields: A list of field names to process for note elements.
    """
    for field in fields:
        field_value = safe_str(row.get(field))
        if field_value:  # Add note only if there's a value
            note_element = Element('note')
            c03.append(note_element)
            # Utilizing add_elements to add the note content
            add_elements(note_element, 'p', [
                         {'text': f"{field}: {field_value}"}])


def add_container_elements(c03, row, container_types):
    """
    Adds container elements to the c03 XML element based on specified container types.

    Parameters:
    - c03: The c03 XML element being processed.
    - row: The row data from which to extract information.
    - container_types: A list of container types (e.g., ['box', 'folder', 'roll']) to process.
    """
    elements_info = []

    for container_type in container_types:
        container_key = f'AAA {container_type} #'
        container_value = safe_str(row.get(container_key))
        if container_value:  # Add only if there's a value
            elements_info.append(
                {'text': container_value, 'attrib': {'type': container_type}})

    add_elements(c03, 'container', elements_info, check_empty=True)
