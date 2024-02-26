#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import ast

def read_lesion_csv(file_path):
    # Define column names
    column_names = ['x', 'y', 'z', 'Index']
    
    # Read CSV into DataFrame
    df = pd.read_csv(file_path, names=column_names, header=0, dtype={'Index': str})
    
    return df


def transform_centroid(centroid, transform):
    """Applies the transformation to the given centroid coordinates."""
    # If the centroid is a string representation of a tuple, convert it to an actual tuple
    if isinstance(centroid, str):
        centroid = ast.literal_eval(centroid)
    return transform.TransformPoint(centroid)


def create_transformed_dataframe(df_file, transform):
    """Creates a new DataFrame with transformed coordinates."""
    df = read_lesion_csv(df_file)
    
    # Ensure numerical values for coordinates
    df[['x', 'y', 'z']] = df[['x', 'y', 'z']].astype(float)
    
    # Get transformed coordinates for each centroid
    transformed_coords = [transform_centroid(centroid, transform) for centroid in df[['x', 'y', 'z']].values]

    # Create the new DataFrame
    transformed_df = pd.DataFrame(transformed_coords, columns=['x', 'y', 'z'])
    transformed_df['Index'] = df['Index']

    return transformed_df