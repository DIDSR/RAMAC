


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



def transform_physical_to_index(image, df_file_or_df):
    """
    Transform physical coordinates to voxel indices using SimpleITK.

    Parameters:
        image (SimpleITK.Image): The image containing the spatial information.
        df_file_or_df (str or pandas.DataFrame): The path to the CSV file containing physical coordinates,
                                                   or a DataFrame containing the physical coordinates directly.

    Returns:
        pandas.DataFrame: DataFrame containing voxel indices.
    """
    # If df_file_or_df is a string, assume it's a CSV file path and read it into a DataFrame
    if isinstance(df_file_or_df, str):
        df = read_lesion_csv(df_file_or_df)
    else:
        # Otherwise, assume it's already a DataFrame
        df = df_file_or_df
    
    # Create an empty list to store voxel coordinates
    voxel_coords = []

    # Loop through each row in the DataFrame
    for index, row in df.iterrows():
        # Extract the physical coordinates from the DataFrame
        physical_coords = [row['x'], row['y'], row['z']]
        # Transform physical coordinates to voxel index using SimpleITK
        index_coords = image.TransformPhysicalPointToIndex(physical_coords)
        # Append the voxel index coordinates to the list
        voxel_coords.append(index_coords)

    # Create a new DataFrame to store the voxel coordinates
    df_voxel = pd.DataFrame(voxel_coords, columns=['voxel_x', 'voxel_y', 'voxel_z'])

    # If the input DataFrame contains an 'Index' column, keep it alongside the voxel coordinates
    if 'Index' in df.columns:
        df_voxel['Index'] = df['Index'].values
    else:
        # Otherwise, add an 'Index' column and assign incremental indices starting from 1
        df_voxel['Index'] = range(1, len(voxel_coords) + 1)

    return df_voxel
