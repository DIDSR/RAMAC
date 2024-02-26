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
from utils import *
from registration import *
from correspondence_csv_input import *
from transform_coordinates import *
from merge_dataframe import *
import warnings


# In[2]:


# Filter out UserWarning temporarily
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


# In[3]:


# TODO: fix to use relative imports
#import sys
#sys.path.append("../ramac")
#from utils import numpy_array_to_sitk, numpy_points_to_sitk

def insert_sphere_in_numpy_array(arr,centroid,radius,intensity):
    """
    Inserts spheres defined by centroid and radius into numpy array x
    
    """
    [xx,yy,zz] = np.meshgrid(*[np.arange(y) for y in arr.shape])
    lesion = np.zeros(arr.shape)
    lesion[((xx-centroid[0])**2+(yy-centroid[1])**2+(zz-centroid[2])**2)<radius**2] = intensity
    
    return arr + lesion


def create_phantom_shepplogan():
    """
    Creates a Shepp-Logan test phantom with two inserted lesions

    Parameters
    ----------
    None.

    Returns
    -------
    phantom: sitk.Image

    """
    
    # size and pixel spacing of the phantom
    phantom_shape = (128, 128, 128)
    spacing = (1.,) * 3
    
    # create shepp logan test phantom
    phantom = shepp_logan(phantom_shape)
    
    # lesion parameters
    lesion_coords = [(50, 64, 100), (80, 64, 20)]
    lesion_radii = [3, 8]
    lesion_intensity = [0.5, 1]
    lesion_index = [1,2]
    
    # inserts lesion
    for ind, lesions in enumerate(lesion_coords):
        phantom = insert_sphere_in_numpy_array(phantom,lesion_coords[ind],lesion_radii[ind],lesion_intensity[ind])
        
    phantom = numpy_array_to_sitk(phantom)
    lesions = numpy_points_to_sitk(lesion_coords,phantom)
        
    return phantom, lesions


##In SimpleITK, when we combine multiple transformations into a composite transform, the transformations are applied in the reverse order

import SimpleITK as sitk

def transform_phantom(phantom, lesions):
    """
    Takes as input phantom and lesions generated from create_phantom_... and applies known rotation and translation in sitk
    
    Parameters
    ----------
    phantom : SimpleITK.Image
        The original phantom image.
    lesions : list of SimpleITK.Point3D
        List of lesion points in the original phantom coordinate system.

    Returns
    -------
    transformed_phantom : SimpleITK.Image
        The transformed phantom image.
    transformed_lesions : list of SimpleITK.Point3D
        List of transformed lesion points.
    known_transformation : SimpleITK.CompositeTransform
        The known composite transformation applied to the phantom and lesions.

    """
    # Define known rotation (30 degrees around y-axis) and translation (shift along x-axis)
    rotation = sitk.Euler3DTransform()
    rotation.SetRotation(0, np.pi/6, 0)  # Rotate 30 degrees around y-axis
    
    translation = sitk.TranslationTransform(3)  # Specify translation along x-axis
    translation.SetOffset((3,0,0))
    
    # Combine rotation and translation into a composite transform
    composite_transform = sitk.CompositeTransform([translation, rotation])
    
    # Convert size vector to list of integers
    size = [int(s) for s in phantom.GetSize()]
    
    # Convert output origin to tuple of floats
    output_origin = tuple(phantom.GetOrigin())
    
    # Convert output spacing to tuple of floats
    output_spacing = tuple(phantom.GetSpacing())
    
    # Apply transformation to phantom
    transformed_phantom = sitk.Resample(phantom, size, composite_transform, sitk.sitkLinear, output_origin, output_spacing, phantom.GetDirection(), 0.0, phantom.GetPixelID())
    
    # Apply transformation to lesions
    transformed_lesions = [composite_transform.TransformPoint(p) for p in lesions]
    
    return transformed_phantom, transformed_lesions, composite_transform


# In[13]:


def applied_transform(transform):
    print("Transformation Parameters:")
    print(transform.GetParameters())

def test_transform_phantom():
    # Create the original phantom
    original_phantom, original_lesions = create_phantom_shepplogan()
    
    # Transform the phantom
    transformed_phantom, transformed_lesions, known_transformation = transform_phantom(original_phantom, original_lesions)
    
    # Visualize the transformation parameters separately
    print("Known Transformation Parameters:")
    applied_transform(known_transformation.GetNthTransform(1))  # Assuming rotation is the first transformation
    print("Known Transformation Parameters:")
    applied_transform(known_transformation.GetNthTransform(0))  # Assuming translation is the second transformation
    
    # Print original and transformed lesion coordinates
    print("Original Lesions:", original_lesions)
    print("Transformed Lesions:", transformed_lesions)

# Run test script
test_transform_phantom()


# ## To cross check whether the applied transformation is correct or not

# In[5]:


import numpy as np

# Define the original lesion coordinates
original_lesions = [(50.0, 64.0, 100.0), (80.0, 64.0, 20.0)]

# Define the angle of rotation in radians
angle = np.pi/6  # 30 degrees in radians

# Define the rotation matrix around the y-axis
rotation_matrix = np.array([
    [np.cos(angle), 0, np.sin(angle)],
    [0, 1, 0],
    [-np.sin(angle), 0, np.cos(angle)]
])

# Define the translation vector
translation_vector = np.array([3, 0, 0])  # Translation along the x-axis

# Apply rotation to each lesion point
transformed_lesions_manual = []
for lesion in original_lesions:
    # Convert the lesion coordinates to a numpy array
    point = np.array(lesion)
    # Apply rotation
    transformed_point = np.dot(rotation_matrix, point)
    # Apply translation
    transformed_point += translation_vector
    transformed_lesions_manual.append(tuple(transformed_point))

print("Transformed Lesions (Manual Calculation):", transformed_lesions_manual)


# In[ ]:




