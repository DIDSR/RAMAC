#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd

def merge_indices(df):
    """
    Merge 'Fixed Index' and 'Reg Index' columns into 'Correspondence Index' column.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing 'Fixed Index' and 'Reg Index' columns.

    Returns:
        pandas.DataFrame: The DataFrame with a new 'Correspondence Index (F, M)' column 
                          containing tuples of corresponding indices.
    """
    # Create a new column 'Correspondence Index' by merging 'Fixed Index' and 'Reg Index' values
    df['Correspondence Index (F, M)'] = df.apply(lambda row: (row['Fixed Index'], row['Reg Index']), axis=1)
    # Keep only the 'Updated Index' and 'Correspondence Index' columns
    df = df[['Updated Index', 'Correspondence Index (F, M)']]
    return df


