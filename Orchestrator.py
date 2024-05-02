config_file_path = r'C:\Users\angel\OneDrive\Desktop\Capstone\Orchestrator\Config.txt'

import os
from datetime import datetime
import pandas as pd

def read_config(file_path):
    params = {}
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('COLLECTION'):
                params['COLLECTION'] = line.split('=')[1].strip().strip("'")
            elif line.startswith('INPUT'):
                params['INPUT'] = line.split('=')[1].strip().strip("'")
            elif line.startswith('OUTPUT'):
                params['OUTPUT'] = line.split('=')[1].strip().strip("'")
            elif line.startswith('LOG'):
                params['LOG'] = line.split('=')[1].strip().strip("'")
            elif line.startswith('TEMP'):
                params['TEMP'] = line.split('=')[1].strip().strip("'")
            elif line.startswith('CODE'):
                params['CODE'] = line.split('=')[1].strip().strip("'")
            elif line.startswith('GOOGLEKEY'):
                params['GOOGLEKEY'] = line.split('=')[1].strip().strip("'")
            elif line.startswith('GPTKEY'):
                params['GPTKEY'] = line.split('=')[1].strip().strip("'")
    return params

def create_and_log(params):
    log_path = params.get('LOG')
    if not os.path.exists(log_path):
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'w') as f:  # Creates the file if it does not exist
            pass
    with open(log_path, 'a') as log_file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{timestamp} - Parameters files read properly, values are: COLLECTION={params['COLLECTION']}, INPUT={params['INPUT']}, OUTPUT={params['OUTPUT']}, TEMP={params['TEMP']}, CODE={params['CODE']}"
        log_file.write(log_message + '\n')

config_values = read_config(config_file_path)
create_and_log(config_values)

def log_message(params, message):
    log_path = params['LOG']
    with open(log_path, 'a') as log_file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file.write(f"{timestamp} - {message}\n")

def filter_and_save_csv(params):
    input_path = params['INPUT']
    collection_filter = params['COLLECTION']
    temp_path = params['TEMP']

    # Load the Excel file
    df = pd.read_excel(input_path)

    # Filter the DataFrame based on the COLLECTION value
    if collection_filter != '*':
        collections = collection_filter.split(',')
        df = df[df['Collection'].isin(collections)]
        filter_description = f"filtered by COLLECTION(s) {collection_filter}"
    else:
        filter_description = "all COLLECTIONs included"

    # Create the TEMP directory if it doesn't exist
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    
    # Define the output CSV file path
    base_name = os.path.basename(input_path)
    csv_name = os.path.splitext(base_name)[0] + '.csv'
    csv_path = os.path.join(temp_path, csv_name)

    # Save the DataFrame to CSV
    df.to_csv(csv_path, index=False)
    row_count = len(df.index)
    log_message(params, f"CSV file created at {csv_path}, {filter_description}, with {row_count} rows.")

    return csv_path

csv_file_path = filter_and_save_csv(config_values)
print(f"Filtered data saved to CSV at: {csv_file_path}")


import os
import subprocess
from datetime import datetime

def log_message(params, message):
    """Log a message with a timestamp to the log file specified in params."""
    log_path = params['LOG']
    with open(log_path, 'a', encoding='utf-8') as log_file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file.write(f"{timestamp} - {message}\n")

def execute_scripts_from_config_code(params, config_code_path):
    """Reads script configuration and executes each script only if output file does not exist, logging each execution."""
    code_dir = params['CODE']
    temp_path = params['TEMP']
    input_csv_basename = os.path.basename(params['INPUT']).replace('.xlsx', '.csv')
    input_csv = os.path.join(temp_path, input_csv_basename)
    current_dir = os.getcwd()  # Save the current directory

    with open(config_code_path, 'r') as file:
        for line in file:
            if line.strip():
                script_rel_path, output_file_name = line.strip().split(',')
                script_path = os.path.join(code_dir, script_rel_path)
                output_csv = os.path.join(temp_path, output_file_name)

                # Check if the output file already exists
                if os.path.exists(output_csv):
                    log_message(params, f"Skipped: {script_path} - Output file already exists: {output_csv}")
                    print(f"Skipped: {script_path} - Output file already exists: {output_csv}")
                    continue

                # Prepare command based on specific script handling
                if 'get_coords.py' in script_path:
                    google_key = params['GOOGLEKEY']
                    additional_path = os.path.join(os.path.dirname(os.path.dirname(code_dir)), 'Geocoding', 'relative_locations.csv')
                    command = f'python "{script_path}" "{input_csv}" "{output_csv}" "{google_key}" "{additional_path}"'
                elif script_path.endswith(('Materialtype.py', 'Media.py', 'Settype.py')):
                    mapped_genre_form_path = os.path.join(code_dir, 'Material_Media_Set', 'Mapped_genre_form.xlsx')
                    command = f'python "{script_path}" "{input_csv}" "{mapped_genre_form_path}" "{output_csv}"'
                elif 'Client.py' in script_path:
                    gpt_key = params['GPTKEY']
                    os.chdir(os.path.dirname(script_path))  # Change directory to the script's directory
                    command = f'python "{os.path.basename(script_path)}" "{input_csv}" "{output_csv}" "{gpt_key}"'
                else:
                    command = f'python "{script_path}" "{input_csv}" "{output_csv}"'
                
                try:
                    print(f"Executing: {command}")
                    subprocess.run(command, check=True, shell=True)
                    print("Execution successful.")
                    log_message(params, f"Executed: {command} - Success")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to execute script: {script_path}")
                    print("Error:", e)
                    log_message(params, f"Failed to execute script: {script_path} - Error: {e}")
                finally:
                    if 'Client.py' in script_path:
                        os.chdir(current_dir)  # Change back to the original directory

def main():
    config_code_path = os.path.join(config_values['CODE'], 'Config_code.txt')
    execute_scripts_from_config_code(config_values, config_code_path)

if __name__ == '__main__':
    main()


import pandas as pd
import os
from datetime import datetime

def log_message(params, message):
    log_path = params['LOG']
    with open(log_path, 'a') as log_file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file.write(f"{timestamp} - {message}\n")

def merge_csv_files(params, initial_csv, csv_dir):
    # Define columns to remove for each specific file and general unwanted columns
    columns_to_remove = {
        'Set_type.csv': ['coll code', 'Collection', 'Project name', 'Project number', 'Street address', 'City', 'County',
                         'State/Province', 'Country', 'FAST Geographic', 'Primary archt/firm', 'Collaborators:', 'Client',
                         'Contributor notes', 'Notes', 'Number of items', 'AAA box #', 'AAA folder #', 'AAA roll #',
                         'Date on drawings', 'Date normalized', 'Media', 'Material types:', 'Processor',
                         'Processing completion date', 'Entry date:', 'Rev. date:', 'Pres. notes:', 'treatment completed A',
                         'treatment completed B', 'treatment completed C', 'treatment completed D', 'treatment completed E',
                         'Accession #', 'Holding institution:'],
        'Media.csv': ['coll code', 'Collection', 'Project name', 'Project number', 'Street address', 'City', 'County',
                      'State/Province', 'Country', 'FAST Geographic', 'Primary archt/firm', 'Collaborators:', 'Client',
                      'Contributor notes', 'Notes', 'Number of items', 'AAA box #', 'AAA folder #', 'AAA roll #',
                      'Date on drawings', 'Date normalized', 'Material types:', 'Set type', 'Processor',
                      'Processing completion date', 'Entry date:', 'Rev. date:', 'Pres. notes:', 'treatment completed A',
                      'treatment completed B', 'treatment completed C', 'treatment completed D', 'treatment completed E',
                      'Accession #', 'Holding institution:'],
        'Material_type.csv': ['coll code', 'Collection', 'Project name', 'Project number', 'Street address', 'City', 'County',
                              'State/Province', 'Country', 'FAST Geographic', 'Primary archt/firm', 'Collaborators:', 'Client',
                              'Contributor notes', 'Notes', 'Number of items', 'AAA box #', 'AAA folder #', 'AAA roll #',
                              'Date on drawings', 'Date normalized', 'Media', 'Set type', 'Processor',
                              'Processing completion date', 'Entry date:', 'Rev. date:', 'Pres. notes:', 'treatment completed A',
                              'treatment completed B', 'treatment completed C', 'treatment completed D', 'treatment completed E',
                              'Accession #', 'Holding institution:']
    }

    # Load the initial CSV file
    # Load the initial CSV file
    try:
        df_main = pd.read_csv(initial_csv, usecols=['unique ID', 'coll code', 'Collection','Holding institution:','AAA box #','AAA folder #','AAA roll #','Accession #','Contributor notes','Date normalized','Date on drawings','FAST Geographic','Number of items','Pres. notes:','Processing completion date','Processor','Project number','State/Province','Street address','treatment completed A','treatment completed B','treatment completed C','treatment completed D','treatment completed E'])
        df_main = df_main.loc[:, ~df_main.columns.str.contains('Unnamed')]
        log_message(params, "Loaded initial CSV file successfully.")
    except Exception as e:
        error_msg = f"Error loading initial columns from {initial_csv}: {e}"
        print(error_msg)
        log_message(params, error_msg)
        return

    # Iterate through the CSV files in the directory
    for filename in os.listdir(csv_dir):
        if filename.endswith('.csv') and filename != os.path.basename(initial_csv):
            file_path = os.path.join(csv_dir, filename)
            try:
                # Try reading with utf-8, if fails, try a different encoding
                try:
                    df_temp = pd.read_csv(file_path)
                except UnicodeDecodeError:
                    df_temp = pd.read_csv(file_path, encoding='iso-8859-1')  # or 'windows-1252'

                df_temp = df_temp.loc[:, ~df_temp.columns.str.contains('Unnamed')]
                # Remove unnecessary columns if the file matches one of the specified ones
                if filename in columns_to_remove:
                    df_temp = df_temp.drop(columns=[col for col in columns_to_remove[filename] if col in df_temp.columns], errors='ignore')
                # Ensure 'unique ID' exists in df_temp
                if 'unique ID' not in df_temp.columns:
                    error_msg = f"'unique ID' column not found in {filename}. Available columns are: {df_temp.columns.tolist()}"
                    print(error_msg)
                    log_message(params, error_msg)
                    continue
                # Merge with the main DataFrame
                df_main = pd.merge(df_main, df_temp, on='unique ID', how='left')
                log_message(params, f"Merged {filename} successfully.")
            except Exception as e:
                error_msg = f"Failed to merge {filename}: {e}"
                print(error_msg)
                log_message(params, error_msg)

    # Save the merged DataFrame to Excel
    # Save the merged DataFrame to Excel
    output_excel_path = params['OUTPUT']  # Directly using the OUTPUT path as specified
    try:
        os.makedirs(os.path.dirname(output_excel_path), exist_ok=True)  # Ensure the directory exists
        df_main.to_excel(output_excel_path, index=False)
        success_msg = f"Data saved to Excel at: {output_excel_path}"
        print(success_msg)
        log_message(params, success_msg)
    except Exception as e:
        error_msg = f"Failed to save Excel file: {e}"
        print(error_msg)
        log_message(params, error_msg)

# Setup and execution
initial_csv_base = os.path.basename(config_values['INPUT']).replace('.xlsx', '.csv')
initial_csv = os.path.join(config_values['TEMP'], initial_csv_base)
csv_dir = config_values['TEMP']
merge_csv_files(config_values, initial_csv, csv_dir)
