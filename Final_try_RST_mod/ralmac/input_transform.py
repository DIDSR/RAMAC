#!/usr/bin/env python
# coding: utf-8

# In[ ]:

#import sys
#sys.path.append("../ralmac")
from phantominator import shepp_logan
from utils import *


import SimpleITK as sitk
import numpy as np

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
    lesion_coords = [(64,50,60), (64,80,20)]
    lesion_radii = [3, 8]
    lesion_intensity = [0.5, 1]
    lesion_index = [1,2]
    
    # inserts lesion
    for ind, lesions in enumerate(lesion_coords):
        phantom = insert_lesion(phantom,lesion_coords[ind],lesion_radii[ind])
        
    phantom = numpy_array_to_sitk(phantom)
    lesions = numpy_points_to_sitk(lesion_coords,phantom)
        
    return phantom, lesions

##In SimpleITK, when we combine multiple transformations into a composite transform, the transformations are applied in the reverse order

def transform_phantom(phantom, lesions):
    """
    Takes as input phantom and lesions generated from create_phantom_... and applies known rotation and translation in sitk
    
    Parameters
    ----------
    phantom : SimpleITK.Image
        The original phantom image.
    lesions : list of SimpleITK point coordinates
        List of lesion points in the original phantom coordinate system.

    Returns
    -------
    transformed_phantom : SimpleITK.Image
        The transformed phantom image.
    transformed_lesions : list of SimpleITK point coordinates
        List of transformed lesion points.
    known_transformation : SimpleITK.CompositeTransform
        The known composite transformation applied to the phantom and lesions.
        Composite transformations are applied in stack order

    """
    # Define known rotation (30 degrees around y-axis) and translation (shift along x-axis)
    rotation = sitk.Euler3DTransform()
    rotation.SetRotation(np.pi/6,0, 0)  # Rotate 30 degrees around x axis i.e in yz plane
    
    rotation_1 = sitk.Euler3DTransform() # Needed only for visualization of the moving image
    rotation_1.SetRotation(0,0, np.pi/6) 
    
    translation = sitk.TranslationTransform(3)  # Specify translation. Translation is done along y and z axes
    translation.SetOffset((0,10,15))
    
    translation_1 = sitk.TranslationTransform(3)  # Needed only for visualization of the moving image
    translation_1.SetOffset((-15,-10,0))
    
    # Combine rotation and translation into a composite transform
    composite_transform = sitk.CompositeTransform([translation, rotation])
    
    composite_transform_1 = sitk.CompositeTransform([translation_1, rotation_1])
  
    
    # Convert size vector to list of integers
    size = [int(s) for s in phantom.GetSize()]
    
    # Convert output origin to tuple of floats
    output_origin = tuple(phantom.GetOrigin())
    
    # Convert output spacing to tuple of floats
    output_spacing = tuple(phantom.GetSpacing())
    
    # Apply transformation to phantom
    transformed_phantom = sitk.Resample(phantom, size, composite_transform, sitk.sitkLinear, output_origin, output_spacing, 
                                        phantom.GetDirection(), 0.0, phantom.GetPixelID())
    
    
    # Apply transformation to lesions
    transformed_lesions_1 = [composite_transform_1.TransformPoint(p) for p in lesions]
    
    transformed_lesions = [composite_transform.TransformPoint(p) for p in lesions]
    
    return transformed_phantom, transformed_lesions, transformed_lesions_1, composite_transform




