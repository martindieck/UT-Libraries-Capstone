import configparser
import os
import pandas as pd
import sys
import re
import json
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Access the GPT API key
api_key = os.getenv('GPT_API_KEY')
if api_key:
    print("Successfully received API Key")
else:
    print("API Key not found. Please check your .env file.")

client = OpenAI(api_key=api_key)

llm_instruction = "You have 2 tasks: identify and format. Below are the instructions for both.\n\nIdentify and Reformat Instructions:\nFind the entities in the entry and reformat them. If it is a person, format their name as [title] [first name or initial] [middle name or initial] [last name]. There will sometimes be multiple people but only one given name like Dang, William (Mr. and Mrs.). If this is the case, create multiple entities for each title: Mr. William Dang, and Mrs. William Dang.\nEsq. is a person's title\nGive me the JSON Object that stores each entity and its type. The types you can use are person and corporate.\n\nFor example:\nUrshel, Mr. and Mrs. C. F. would be {\"Mr. C. F. Urshel\": \"person\", \"Mrs. C. F. Urshel\": \"person\"}\nBexar County would be {\"Bexar County\": \"corporate\"}\n"

llm_cache = {}


def update_cache_from_json(json_file_path):
        # Loading the JSON file
        data = json.load(open(json_file_path))


        # Check if the data needs any transformation or direct update
        if isinstance(data, dict):
            # Direct update if the data is already a dictionary
            llm_cache.update(data)
        else:
            # Convert data to required format if not already a dictionary
            transformed_data = {item: 'person' for item in data}  # Adjust transformation as needed
            llm_cache.update(transformed_data)


def read_ini_file_strip_quotes(filepath):
    """
    Reads an INI file and extracts all sections, stripping quotes from keys and values.

    Args:
        filepath (str): Path to the INI file.

    Returns:
        dict: A dictionary with all sections, keys, and values stripped of quotes.
    """
    config = configparser.ConfigParser()
    config.read(filepath)
    
    # Initialize an empty dictionary to store the cleaned data
    cleaned_config = {}
    
    # Iterate over all sections in the INI file
    for section in config.sections():
        # Apply stripping of quotes to each key and value in the section
        cleaned_config[section] = {key.strip('"'): value.strip('"') for key, value in config[section].items()}
        cleaned_config[section] = {key.strip('\''): value.strip('\'') for key, value in config[section].items()}
    
    return cleaned_config


def contains_any_flag(entry, flag_dicts, debug = False):
    """
    Check if any flag from any dictionary is a substring or an exact match in the entry,
    depending on the flag's specified match type ('exact' or not specified as substring).
    Args:
        entry (str): The text entry to check.
        flag_dicts (list of dicts): List of dictionaries with flags as keys and 'exact' or 'substring' as values.
    Returns:
        bool: True if any appropriate flag is found in the entry, False otherwise.
    """
    entry_lower = entry.lower()
    found = False
    for flags in flag_dicts:
        for flag, match_type in flags.items():
            flag_lower = flag.lower()
            if match_type == 'exact':
                # Use regex to find exact matches (consider word boundaries)
                if re.search(r'\b' + re.escape(flag_lower) + r'\b', entry_lower):
                    if debug:
                        print(f"Exact match for {entry} found: {flag}")
                    found = True
            else:
                # Default to substring match if not 'exact'
                if flag_lower in entry_lower:
                    if debug:
                        print(f"Substring match for {entry} found: {flag}")
                    found = True
    return found


def is_complex_context(phrase, match_start, match_end):
    """
    Determines if the context around a matched phrase suggests it is part of a complex structure.
    """
    # Check preceding text for complexity indicators (e.g., commas, parentheses)
    preceding_text = phrase[:match_start].strip()
    if preceding_text.endswith(',') or '(' in preceding_text:
        return True

    # Check following text for complexity indicators (e.g., commas, parentheses)
    following_text = phrase[match_end:].strip()
    if following_text.startswith(',') or '(' in following_text:
        return True

    return False

def check_ands(phrase, debug = False):
    pattern = r'\b([A-Za-z]+)\s+(and|&)\s+([A-Za-z]+)\b'
    matches = re.finditer(pattern, phrase)
    flagged = False
    for match in matches:
        if not is_complex_context(phrase, match.start(), match.end()):
            if debug:
                print(f"Flagged: {phrase} -> Match: {match.group(0)}")
            flagged = True
            return flagged
    if not flagged:
        if debug:
            print(f"Not Flagged: {phrase}")
    return flagged

def check_single_word(entry, debug = False):
    """
    Check if the given entry is a single word, considering more complex word definitions.
    
    Args:
        entry (str): The text entry to check. Strips leading/trailing whitespace.
        
    Returns:
        bool: True if the entry is a single word, False otherwise.
    """
    entry = entry.strip()
    # This pattern matches words that may include hyphens, apostrophes and Unicode letters
    if re.fullmatch(r"[\w'-]+", entry, re.UNICODE):
        if debug:
            print("single word: " + entry)
        return True
    return False

def get_llm_output(input_text, instruction, debug = False):
    if input_text in llm_cache:
        if debug:
            print("Using cached data: " + input_text)
        return llm_cache[input_text]
    else:
        try:
            completion = client.chat.completions.create(
                model="ft:gpt-3.5-turbo-0125:personal:pcl-ft-2:9G7ldf6T",
                messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": input_text}
                ]
            )
            result = completion.choices[0].message.content if completion.choices else ''
            llm_cache[input_text] = result  # Cache the result
            return result
        except Exception as e:  # Catch any kind of exception, not just JSON-related
            print("Error during LLM output retrieval:", e)
            return '{"Flag": "API Call Failed"}'  # Indicates an API failure


def update_dataframe_from_llm(df, index, entry, processed_data, all_corp_rules, persons_name_flags, debug = False):
    """
    Updates the DataFrame based on processed data from the LLM.

    Args:
    - df (pd.DataFrame): The DataFrame to update.
    - index (int): The index of the DataFrame row to update.
    - entry (str): The original text entry processed by the LLM.
    - processed_data (dict): The data returned from the LLM, structured as key-value pairs.
    - all_corp_rules (list of dict): Rules to identify corporate entities.
    - persons_name_flags (dict): Rules to identify flagged person entries.

    Returns:
    - None: Modifies the DataFrame in place.
    """
    # print(f"Processed data for entry '{entry}': {processed_data}")

    if "Flag" in processed_data:
        if debug:
            print(f"Warning: {processed_data['Flag']} for row {index}")
        df.at[index, 'Client1[Name]'] = entry  # Use the original entry if there's an issue
        df.at[index, 'Client1[Type]'] = 'corporate'  # Default type if processing failed
        df.at[index, 'Client1[Name]_flag'] = 1  # Flag this entry as problematic
    else:
        for idx in range(1, len(processed_data)//2 + 1):  # Determine how many entities there are
            name_key = f'Client{idx}[Name]'
            type_key = f'Client{idx}[Type]'
            name = processed_data[name_key]
            entity_type = processed_data[type_key]

            df.at[index, name_key] = name
            df.at[index, type_key] = entity_type

            # Check if the entity should be flagged based on its type
            if entity_type == "corporate":
                if contains_any_flag(name, all_corp_rules):
                    df.at[index, f'Client{idx}_flag'] = 1
            elif entity_type == "person":
                if contains_any_flag(name, [persons_name_flags]):
                    df.at[index, f'Client{idx}_flag'] = 1
            if debug:
                print(f"Updated row {index} with {name} as {entity_type}")

def process_json(output_json):
    try:
        print(output_json)
        data = json.loads(output_json)
        entity_dict = {}
        for idx, (name, entity_type) in enumerate(data.items(), start=1):
            entity_dict[f'Client{idx}[Name]'] = name
            entity_dict[f'Client{idx}[Type]'] = entity_type
        return entity_dict
    except json.JSONDecodeError:
        return {"Flag": "Invalid JSON Format"}

def main():

    """Get input data"""
    # Check if the correct number of arguments are passed
    if len(sys.argv) != 3:
        print("Usage: python Client.py <input xlsx> <output csv>")
        sys.exit(1)

    # Input and output file paths
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Read the Excel file
    try:
        original_df = pd.read_excel(input_file, sheet_name='database', usecols=['unique ID', 'Client'])
        print(f"Read {len(original_df)} rows and {len(original_df.columns)} columns from {input_file}")
    except Exception as e:
        print(f"Failed to read from {input_file}. Error: {e}")
        sys.exit(1)

    """----------------"""
    # create new df with a temporary flag section
    df = original_df

    # config
    current_directory = os.getcwd()

    # TODO: Work on this functionality
    # update_cache_from_json('rules/womens_names.json')

    # load name flag rules
    name_flagging = read_ini_file_strip_quotes(current_directory + '/rules/name_flagging.ini')
    corporate_name_flags = dict(name_flagging['corporate flag indicators']) 
    uncertain_original_data = dict(name_flagging['uncertain original data'])
    persons_name_flags = dict(name_flagging['persons flags'])

    # load corporate cleaning data
    corporate_cleaning_rules = read_ini_file_strip_quotes(current_directory + '/rules/corporate_cleaning_rules.ini')
    corp_indicators = dict(corporate_cleaning_rules['corporate indicators'])
    known_corps = dict(corporate_cleaning_rules['known corporations'])

    # load persons cleaning data

    # Initialize potential dynamic columns
    max_entity_count = 10
    for i in range(1, max_entity_count+1):
        df[f'Client{i}[Name]'] = None
        df[f'Client{i}[Type]'] = None
        df[f'Client{i}_flag'] = 0

    # List of dictionaries to check against
    all_corp_rules = [corp_indicators, known_corps, corporate_name_flags, uncertain_original_data]

    api_counter = 0

    # Iterate through each row in the DataFrame and check for flags
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing DataFrame"):
        curr_entry = row['Client']
        if pd.isna(curr_entry):
            continue

        # Check if it is a corpname based on predefined rules
        elif contains_any_flag(curr_entry, all_corp_rules):
            # Flag any known problems with the corpname
            if contains_any_flag(curr_entry, [corporate_name_flags], debug=False):
                df.at[index, 'Client1[Name]_flag'] = 1

            df.at[index, 'Client1[Name]'] = row['Client']
            df.at[index, 'Client1[Type]'] = 'corporate'

        # If not cleaned with predefined rules, check the data for a rule
        else:
            if check_ands(curr_entry):
                df.at[index, 'Client1[Name]_flag'] = 1
                df.at[index, 'Client1[Name]'] = curr_entry
                df.at[index, 'Client1[Type]'] = 'corporate'

            elif check_single_word(curr_entry):
                df.at[index, 'Client1[Name]_flag'] = 1
                df.at[index, 'Client1[Name]'] = curr_entry
                df.at[index, 'Client1[Type]'] = 'corporate'
        
            else:
                api_counter += 1

                json_output = get_llm_output(curr_entry, llm_instruction)
                processed_data = process_json(json_output)
                update_dataframe_from_llm(df, index, curr_entry, processed_data, all_corp_rules, persons_name_flags)

                if api_counter == 100:
                    break
            
    print("LLM API called" , api_counter , "times.")

    # Remove columns if the entire [Name] column is empty
    for i in range(1, max_entity_count+1):
        if df[f'Client{i}[Name]'].isna().all():
            del df[f'Client{i}[Name]']
            del df[f'Client{i}[Type]']
            del df[f'Client{i}_flag']

    # Write DataFrame to CSV
    try:
        df.to_csv(output_file, index=False)
        print(f"Data has been written to {output_file}")
    except Exception as e:
        print(f"Failed to write to {output_file}. Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
