import pandas as pd

def get_collection(collection_code):
    df = pd.read_csv('collections.csv')
    df = df.fillna('')
    return df[df['coll code'] == collection_code]