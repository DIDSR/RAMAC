#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import ast

def read_lesion_csv(file_path):
    """
    Read lesion data from a CSV file into a DataFrame.

    Parameters:
        file_path (str): The path to the CSV file containing lesion data.

    Returns:
        pandas.DataFrame: A DataFrame containing the lesion data.
    """
    # Define column names
    column_names = ['x', 'y', 'z', 'Index']
    
    # Read CSV into DataFrame
    df = pd.read_csv(file_path, names=column_names, header=0, dtype={'Index': str})
    
    return df


def transform_centroid(centroid, transform):
    """
    Apply a transformation to a given centroid.

    Parameters:
        centroid (tuple or str): The centroid coordinates as a tuple or string representation.
        transform (SimpleITK.Transform): The transformation to apply.

    Returns:
        tuple: The transformed centroid coordinates.
    """
    # If the centroid is a string representation of a tuple, convert it to an actual tuple
    if isinstance(centroid, str):
        centroid = ast.literal_eval(centroid)
    return transform.TransformPoint(centroid)


def create_transformed_dataframe(df_file, transform):
    """
    Create a new DataFrame with transformed coordinates.

    Parameters:
        df_file (str): The path to the CSV file containing the original lesion data.
        transform (SimpleITK.Transform): The transformation to apply to the coordinates.

    Returns:
        pandas.DataFrame: A DataFrame containing the transformed lesion data.
    """
    df = read_lesion_csv(df_file)
    
    # Ensure numerical values for coordinates
    df[['x', 'y', 'z']] = df[['x', 'y', 'z']].astype(float)
    
    # Get transformed coordinates for each centroid
    transformed_coords = [transform_centroid(centroid, transform) for centroid in df[['x', 'y', 'z']].values]

    # Create the new DataFrame
    transformed_df = pd.DataFrame(transformed_coords, columns=['x', 'y', 'z'])
    transformed_df['Index'] = df['Index']

    return transformed_df
