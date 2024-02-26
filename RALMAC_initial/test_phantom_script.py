#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import SimpleITK as sitk
from phantominator import shepp_logan
import matplotlib.pyplot as plt
import skimage
import scipy
import os
import csv
import pandas as pd
from registration import *
from correspondence_csv_input import *
from transform_coordinates import *
from merge_dataframe import *
import warnings

# Filter out UserWarning temporarily
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


# size and pixel spacing of the phantom
phantom_shape = (128, 128, 128)
spacing = (1.,) * 3

# create shepp logan test phantom
phantom = shepp_logan(phantom_shape)

## Function to insert lesions inside phantom

def insert_lesion(x,c,r):
    [xx,yy,zz] = np.meshgrid(*[np.arange(y) for y in x.shape])
    lesion = np.zeros(x.shape)
    lesion[((xx-c[0])**2+(yy-c[1])**2+(zz-c[2])**2)<r**2] = 0.5
    return x+lesion

# insert simulated lesions cordinates
#lesion_coords = [(50, 64, 100), (80, 64, 20)]
lesion_coords = [(10, 10, 20), (50, 50, 20)] 
lesion_radii = [3, 8]
lesion_index = [1, 2]
#lesion_plots = [(100, 50), (20, 80)]  # Coordinates are swapped for plotting

for ll, lesions in enumerate(lesion_coords):
    phantom = insert_lesion(phantom,lesion_coords[ll],lesion_radii[ll])

# Convert phantom to SimpleITK format
fixed_image = sitk.GetImageFromArray(phantom)
fixed_image.SetSpacing(spacing)

#### Let us make the moving)image by transformation

# Define a function to apply rotation and translation to the phantom
def transform_phantom(phantom, rotation_angle, translation):
    # Rotate around the 'x' and 'y' axes
    rotated = scipy.ndimage.rotate(phantom, rotation_angle, axes=(0, 1), reshape=False)
    # Apply translation
    translated = scipy.ndimage.shift(rotated, translation)
    return translated

# Apply the transformation to the phantom
rotation_angle = 30  # 30 degrees
translation = (0, 10, 15)  # Translation in z, y, x
transformed_phantom = transform_phantom(phantom, rotation_angle, translation)

# Convert phantom to SimpleITK format
def array_to_sitk(x):
    x_sitk = sitk.GetImageFromArray(x)
    x_sitk.SetOrigin((0, 0, 0))
    x_sitk.SetSpacing(spacing)
    return x_sitk

# Convert transformed phantom to SimpleITK format
moving_image = array_to_sitk(transformed_phantom)

transformed_lesion_coords = []
for coord in lesion_coords:
    # Convert the tuple to a 3D array
    coord_array = np.array(coord).reshape((1, 1, 3))
    
    # Rotate the coordinates around the x-axis (axis 0) and y-axis (axis 1)
    rotated_coord = scipy.ndimage.rotate(coord_array, rotation_angle, axes=(0, 1), reshape=False)
    
    # Shift the rotated coordinates
    shifted_coord = rotated_coord + np.array(translation).reshape((1, 1, 3))
    
    # Convert back to tuple and append to transformed_lesion_coords
    transformed_lesion_coords.append((shifted_coord[0, 0, 0], shifted_coord[0, 0, 1], shifted_coord[0, 0, 2]))

def save_lesion_coordinates(lesion_coords, lesion_index, filename):
    # Create a DataFrame to store the lesion coordinates and indices
    df = pd.DataFrame({'x': [coord[0] for coord in lesion_coords],
                       'y': [coord[1] for coord in lesion_coords],
                       'z': [coord[2] for coord in lesion_coords],
                       'Index': [str(index) for index in lesion_index]})
    # Write the DataFrame to a CSV file
    df.to_csv(filename, index=False)
    
# Filenames
filename_fixed = 'fixed_coordinates.csv'
filename_moving = 'moving_coordinates.csv'

# Save the fixed lesion coordinates
save_lesion_coordinates(lesion_coords, lesion_index, filename_fixed)

# Save the moving lesion coordinates
save_lesion_coordinates(transformed_lesion_coords, lesion_index, filename_moving)

moving_resampled, [init_transform, final_transform] = registration_3d_rigid_series(fixed_image, moving_image)


final_transform_1 = final_transform.GetInverse()

registered_coordinates = create_transformed_dataframe(filename_moving, final_transform_1)

def save_transformed_dataframe(transformed_df, output_file):
    """Saves the transformed DataFrame to a CSV file."""
    transformed_df.to_csv(output_file, index=False)

# Assuming 'registered_coordinates' is your transformed DataFrame and 'output_file' is the desired filename
save_transformed_dataframe(registered_coordinates, 'registered_coordinates.csv')

threshold = 30  # Set your threshold here
filename_registered = 'registered_coordinates.csv'
# Process correspondences
correspondences, unmatched_names_df1, unmatched_names_df2 = process_lesion_timepoints(filename_fixed, filename_registered, threshold)

plot_lesion_correspondences_timepoints(filename_fixed, filename_registered)
# Create the final DataFrame
final_df = create_final_dataframe_timepoints(correspondences, unmatched_names_df1, unmatched_names_df2, filename_fixed, filename_registered)

df_transformed = merge_indices(final_df)

# Save the resulting DataFrame to a CSV file
df_transformed.to_csv('correspondence_indices.csv', index=False)


# In[ ]:




