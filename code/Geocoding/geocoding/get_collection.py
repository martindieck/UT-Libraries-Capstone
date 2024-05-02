import pandas as pd

def get_collection(collection_code):
    """Function to return the rows belonging to the specified collection.
    Input: Two-letter collection code as string (Ex. AA, FG, etc.)
    Returns: Pandas dataframe containing the specified rows"""

    df = pd.read_csv('collections.csv')
    df = df.fillna('')
    return df[df['coll code'] == collection_code]