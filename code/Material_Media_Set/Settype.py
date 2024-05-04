import pandas as pd
import numpy as np

import sys

if len(sys.argv) != 4:
    print("Usage: python script.py <input_csv> <output_csv>")
    print("Number of arguments:", len(sys.argv))
    print("Argument List:", str(sys.argv))
    sys.exit(1)

# Input and output file paths
input_csv = sys.argv[1]
map_path = sys.argv[2]
output_csv = sys.argv[3]

separators_set = '|'.join([' on', ',', '/', '\n',':','&',' and'])
#print(separators_set)

df = pd.read_csv(input_csv)
# Split the 'Media' column based on the separators
df_split = df['Set type'].str.split(separators_set, expand=True)
# if df_split[17].isna().all():
#     print("All values in column 17 are NaN")
# else:
#     # Display non-NaN values in column 17
#     non_nan_values = df_split.loc[~df_split[17].isna(), 17]
#     print("Non-NaN values in column 17:")
#     print(non_nan_values)
# # Determine the maximum number of columns needed
max_cols = df_split.shape[1]

# Create new column names based on the maximum number of columns
new_cols = [f'Set type[{i+1}]' for i in range(max_cols)]
new_src_cols = [f'Set type_src[{i+1}]' for i in range(max_cols)]
new_flag_cols = [f'Set type[{i+1}][flag]' for i in range(max_cols)]

# Rename the columns
df_split.columns = new_cols 
df_src = pd.DataFrame(columns=new_src_cols)

# Concatenate the original DataFrame with the new columns
df_test = pd.concat([df,df_split, df_src], axis=1)

# Output the DataFrame with the new columns
#df_test.to_csv('outputmedia.csv', index=False)
print(new_cols)
print(new_src_cols)

sheet_name = 'Settype'
#map_path = '/Users/sirikuppili/Desktop/capstone/Mapped_genre□form.xlsx'
df_map2 = pd.read_excel(map_path, sheet_name=sheet_name)

print(df_map2)

for col, src in zip(new_cols, new_src_cols):
    #print(new_cols)
    for index, val in df_test[col].items():
        #print(val)
        #print(df_map2['Set types from Project DB'].values)

        if val in df_map2['Set types from Project DB'].values:
            idx = df_map2[df_map2['Set types from Project DB'] == val].index[0]
            if df_test.at[index, src] != " ":
                df_test.at[index, col] = df_map2.loc[df_map2['Set types from Project DB'] == val, 'genreform'].iloc[0]
                df_test.at[index, src] = df_map2.loc[df_map2['Set types from Project DB'] == val, 'authority'].iloc[0]
                #if pd.notna(df_map2.loc[idx, 'genreform2']):
                  #  df_test.at[index+1, col] = df_map2.loc[idx, 'genreform2']
                  # df_test.at[index+1, src] = df_map2.loc[idx, 'authority2']

# Output the DataFrame with the new column
#print(df_test)
#df_test.to_csv('outputmedia.csv', index=False)
for col,flag in zip(new_cols, new_flag_cols):
    for index, val in df_test[col].items():
        if not pd.isnull(val):  # Check if cell is not empty
            if val in df_map2['genreform'].values:
                df_test.at[index, flag] = '0'
            else:
                df_test.at[index, flag] = '1'

# Output the DataFrame with the new 'flagged' column
df_test.to_csv(output_csv)