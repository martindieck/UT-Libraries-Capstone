import pandas as pd
from dateutil import parser
import sys

# Define timezone information
tzinfos = {
    "CST": -6 * 3600,  # Central Standard Time
    "CDT": -5 * 3600,  # Central Daylight Time
    "EST": -5 * 3600,  # Eastern Standard Time
    "EDT": -4 * 3600,  # Eastern Daylight Time
    "PST": -8 * 3600,  # Pacific Standard Time
    "PDT": -7 * 3600   # Pacific Daylight Time
}

def normalize_date(date):
    """Normalize different date formats to YYYY-MM-DD, using flexible parsing with timezone support."""
    if pd.isna(date):
        return None, 0  # No data to process, flag as 0
    try:
        # Using dateutil.parser to handle different formats and timezone information
        normalized_date = parser.parse(date, fuzzy=True, tzinfos=tzinfos)
        return normalized_date.strftime('%Y-%m-%d'), 0
    except Exception as e:
        print(f"Error processing date {date}: {e}")  # Logging the error
        return None, 1

def main(input_csv_path, output_csv_path):
    # Load the CSV file
    data = pd.read_csv(input_csv_path)

    # Apply the normalization function to the "Entry date:" column
    data['Entry_date_normalized'], data['Entry_date_flag'] = zip(*data['Entry date:'].apply(normalize_date))

    # Select relevant columns to save to a new DataFrame
    output_data = data[['unique ID', 'Entry date:', 'Entry_date_normalized', 'Entry_date_flag']]

    # Save the output DataFrame to the specified CSV file
    output_data.to_csv(output_csv_path, index=False)
    print(f"Data saved to {output_csv_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python Entry_date.py <input_csv_path> <output_csv_path>")
        sys.exit(1)
    
    input_csv_path = sys.argv[1]
    output_csv_path = sys.argv[2]
    main(input_csv_path, output_csv_path)
