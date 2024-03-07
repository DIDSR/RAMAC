#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import SimpleITK as sitk
import skimage
import scipy

def numpy_array_to_sitk(x, spacing=(1.,)*3, origin=(0.,)*3):
    """
    Converts a NumPy array to a SimpleITK image format.

    Args:
        x (np.ndarray): The input NumPy array.
        spacing (tuple, optional): The spacing of the image voxels along each dimension. Defaults to (1., 1., 1.).
        origin (tuple, optional): The origin of the image in physical coordinates. Defaults to (0., 0., 0.).

    Returns:
        SimpleITK.Image: The SimpleITK image representation of the input NumPy array.
    """
    x_sitk = sitk.GetImageFromArray(x)
    x_sitk.SetOrigin(origin)
    x_sitk.SetSpacing(spacing)
    
    return x_sitk

def insert_lesion(x, c, r):
    """
    Inserts a lesion into the given 3D array.

    Args:
        x (np.ndarray): The 3D array representing the phantom.
        c (tuple): The coordinates of the center of the lesion in the format (z, y, x).
        r (float): The radius of the lesion.

    Returns:
        np.ndarray: The modified phantom array with the lesion inserted.
    """
    # Generate meshgrid arrays with the same shape as the input array
    zz, yy, xx = np.meshgrid(np.arange(x.shape[0]), np.arange(x.shape[1]), np.arange(x.shape[2]), indexing='ij')
    
    # Create a mask for the lesion region
    mask = ((zz - c[0]) ** 2 + (yy - c[1]) ** 2 + (xx - c[2]) ** 2) < r ** 2
    
    # Apply the mask to the phantom array
    x[mask] = 0.5
    
    return x


def transform_phantom(phantom, rotation_angle, translation, axes=(1,2)):
    """
    Apply rotation and translation to the phantom.

    Parameters:
        phantom (ndarray): The input phantom.
        rotation_angle (float): The rotation angle in degrees.
        translation (tuple): The translation vector.

    Returns:
        ndarray: The transformed phantom.
    """
    rotated = scipy.ndimage.rotate(phantom, rotation_angle,axes=axes, reshape=False)
    translated = scipy.ndimage.shift(rotated, translation)
    return translated

def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta degrees.

    Parameters:
        axis (list or numpy.ndarray): The axis of rotation.
        theta (float): The angle of rotation in degrees.

    Returns:
        numpy.ndarray: The rotation matrix.
    """
    theta = np.radians(theta)
    axis = np.asarray(axis)
    axis = axis / np.sqrt(np.dot(axis, axis))
    a = np.cos(theta / 2.0)
    b, c, d = -axis * np.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

def apply_rotation_and_translation(lesion_coords, rotation_matrix_x, translation):
    """
    Apply rotation and translation to lesion coordinates.

    Parameters:
        lesion_coords (list of tuples): List of lesion coordinates (x, y, z).
        rotation_matrix_x (numpy.ndarray): Rotation matrix for the x-axis.
        #rotation_matrix_y (numpy.ndarray): Rotation matrix for the y-axis.
        translation (tuple): The translation vector (z, y, x).

    Returns:
        list of tuples: Transformed lesion coordinates.
    """
    transformed_lesion_coords = []

    for coord in lesion_coords:
        rotated_coord = np.dot(rotation_matrix_x, coord)
        transformed_coord = rotated_coord + translation
        transformed_lesion_coords.append(tuple(transformed_coord))

    return transformed_lesion_coords



def numpy_point_to_sitk(xyz, sitk_image):
    """
    Converts a tuple of numpy indices (xyz) to a SimpleITK point.

    Args:
        xyz (tuple): The tuple of integers representing the indices along each axis (x, y, z).
        sitk_image (SimpleITK.Image): The SimpleITK image from which the point is to be extracted.

    Returns:
        SimpleITK.Point: The physical point corresponding to the given numpy indices.
    """
    index = [int(round(i)) for i in xyz]
    sitk_xyz = sitk_image.TransformIndexToPhysicalPoint(index)
    
    return sitk_xyz

def numpy_points_to_sitk(xyzs, sitk_image):
    """
    Converts a list of numpy indices (xyzs) to a list of SimpleITK points.

    Args:
        xyzs (list): A list of tuples, each representing the indices along each axis (x, y, z).
        sitk_image (SimpleITK.Image): The SimpleITK image from which the points are to be extracted.

    Returns:
        list: A list of SimpleITK points corresponding to the given numpy indices.
    """
    sitk_xyzs = []
    
    for ind, xyz in enumerate(xyzs):
        sitk_xyzs.append(numpy_point_to_sitk(xyz, sitk_image))
        
    return sitk_xyzs

def save_lesion_coordinates(lesion_coords, lesion_index, filename):
    """
    Save lesion coordinates to a CSV file.

    Parameters:
        lesion_coords (list of tuples): List of lesion coordinates (x, y, z).
        lesion_index (list of int): List of lesion indices.
        filename (str): The filename for the CSV file.
    """
    df = pd.DataFrame({'x': [coord[0] for coord in lesion_coords],
                       'y': [coord[1] for coord in lesion_coords],
                       'z': [coord[2] for coord in lesion_coords],
                       'Index': [str(index) for index in lesion_index]})
    df.to_csv(filename, index=False)
    
    
def save_transformed_dataframe(transformed_df, output_file):
    """
    Save Transformed DataFrame to a CSV file.

    Parameters:
        transformed_df : DataFrame
            The DataFrame containing the transformed data.

        output_file : str
            The path to the output CSV file.

    Returns:
        None

    Saves:
        The transformed DataFrame to the specified CSV file without index.
    """
    transformed_df.to_csv(output_file, index=False)

    
def applied_transform(transform):
    """
    Applies a transformation and prints its parameters.

    Parameters:
        transform : object
            The transformation object to be applied.

    Returns:
        None

    Prints:
        Transformation Parameters:
        The parameters of the applied transformation.
    """
    print("Transformation Parameters:")
    print(transform.GetParameters())
    
    
def voxel_tuples_from_dataframe(df):
    """
    Extract voxel coordinates as tuples from a DataFrame.

    Parameters:
        df (pandas.DataFrame): DataFrame containing voxel coordinates.

    Returns:
        list: List of tuples containing voxel coordinates.
    """
    return [(row['voxel_x'], row['voxel_y'], row['voxel_z']) for _, row in df.iterrows()]


def round_coordinates_to_integer(coordinates):
    """
    Round each coordinate in a list of tuples to the nearest integer.

    Parameters:
        coordinates (list of tuples): List containing tuples of coordinates.

    Returns:
        list of tuples: List of tuples with each coordinate rounded to the nearest integer.
    """
    rounded_coordinates = [(round(coord[0]), round(coord[1]), round(coord[2])) for coord in coordinates]
    return rounded_coordinates    


# In[ ]:




