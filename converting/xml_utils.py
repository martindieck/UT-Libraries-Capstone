# xml_utils.py
import pandas as pd
from xml.etree.ElementTree import SubElement


def safe_str(val) -> str:
    """Convert non-string, NaN values, and space-only strings to an empty string."""
    if pd.isna(val) or (isinstance(val, str) and val.strip() == ''):
        return ''
    return str(val)


def add_elements(parent, tag, elements_info, check_empty=True):
    """
    Adds subelements to a parent element based on the provided information.

    Parameters:
    - parent: The parent XML element.
    - tag: The tag for the new subelements.
    - elements_info: A list of dictionaries containing info for each subelement.
    - check_empty: Whether to skip adding elements with empty text.
    """
    for elem_info in elements_info:
        if not check_empty or elem_info.get('text', ''):
            subelem = SubElement(
                parent, tag, attrib=elem_info.get('attrib', {}))
            subelem.text = elem_info.get('text', '')
