# Excel to XML Converter

## Overview
This project provides a graphical interface to convert Excel files into XML format. It is particularly useful for processing structured data where XML elements correspond to specific data fields in Excel.

## Features
- **Graphical User Interface**: Easy-to-use interface for selecting and processing Excel files.
- **Custom XML Generation**: Generates XML documents by mapping Excel data to predefined XML structures.

## Dependencies
- Python 3.x
- tkinter
- pandas
- xml.etree.ElementTree
- xml.dom.minidom

## Usage
1. **Start the Application**: Run `ead_converter_with_ui.py` to open the user interface.
2. **Select Excel File**: Use the file dialog to choose an Excel file that contains the data to be converted.
3. **Convert and Save**: The application converts the selected file into XML format and allows you to save the output.

## Modules Description
- `ead_converter_with_ui.py`: Main module with GUI and integration of conversion functionalities.
- `xml_c02.py` & `xml_c03.py`: Handle specific parts of the XML structure based on data rows.
- `xml_utils.py`: Provides utility functions for XML manipulation.

## How to Contribute
Contributions are welcome! You can contribute by improving the GUI, adding more features to XML conversion, or improving the documentation.

