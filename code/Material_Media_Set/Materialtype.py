import pandas as pd
import numpy as np
import sys
import openpyxl

if len(sys.argv) != 4:
    print("Usage: python script.py <input_csv> <output_csv>")
    print("Number of arguments:", len(sys.argv))
    print("Argument List:", str(sys.argv))
    sys.exit(1)

# Input and output file paths
input_csv = sys.argv[1]
map_path = sys.argv[2]
output_csv = sys.argv[3]


df = pd.read_csv(input_csv)


separators = '|'.join([' on ', ',', '/', '\n','and'])

# Split the 'Media' column based on the separators
df_split = df['Material types:'].str.split(separators, expand=True)

# Determine the maximum number of columns needed
max_cols = df_split.shape[1]

# Create new column names based on the maximum number of columns
new_ori_cols = [f'Material types[original][{i+1}]' for i in range(max_cols)]
new_cols = [f'Material types[standard][{i+1}]' for i in range(max_cols)]
new_src_cols = [f'Material types[src][{i+1}]' for i in range(max_cols)]
new_flag_cols = [f'Material types[{i+1}][flag]' for i in range(max_cols)]

# Rename the columns
df_split.columns = new_ori_cols 
df_stand = pd.DataFrame(columns=new_cols)
df_src = pd.DataFrame(columns=new_src_cols)

# Concatenate the original DataFrame with the new columns
df_test = pd.concat([df,df_split,df_stand,df_src], axis=1)

# Output the DataFrame with the new columns
#df_test.to_csv('outputmedia.csv', index=False)
print(new_cols)
print(new_src_cols)

#map_path = '/Users/sirikuppili/Desktop/capstone/Mapped_genre□form.xlsx'
sheet_name = 'Materialtype_new'

df_map2 = pd.read_excel(map_path, sheet_name=sheet_name)

print(df_map2)

for col,std,src in zip( new_ori_cols,new_cols,new_src_cols):
    #print(new_cols)
    for index, val in df_test[col].items():
        if val in df_map2['Material types from Project DB'].values:
            df_test.at[index, std] = df_map2.loc[df_map2['Material types from Project DB'] == val, 'genreform'].iloc[0]
            df_test.at[index, src] = df_map2.loc[df_map2['Material types from Project DB'] == val, 'source'].iloc[0]

# Output the DataFrame with the new columns
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