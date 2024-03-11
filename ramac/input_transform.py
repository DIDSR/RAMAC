#!/usr/bin/env python
# coding: utf-8

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


def generate_visualization_composite_transform(rotation_params, translation_params):
    """
    Generate second composite transformation based on the rotation and translation parameters.

    Parameters
    ----------
    rotation_params : tuple
        Parameters for rotation transformation.
    translation_params : tuple
        Parameters for translation transformation.

    Returns
    -------
    composite_transform_1 : SimpleITK.CompositeTransform
        Second composite transformation.
    """
    # Define rotation transformation for second composite transform
    rotation_1 = sitk.Euler3DTransform()
    rotation_1.SetRotation(*[param for param in reversed(rotation_params)])  # Reverse rotation parameters
    
    # Define translation transformation for second composite transform
    translation_1 = sitk.TranslationTransform(3)
    translation_1.SetOffset([-param for param in reversed(translation_params)])  # Reverse and negate translation parameters
    
    # Combine transformations into composite transform
    #composite_transform_1 = sitk.CompositeTransform([translation_1, rotation_1])
    
    return rotation_1, translation_1

##In SimpleITK, when we combine multiple transformations into a composite transform, the transformations are applied in the reverse order

def transform_phantom(phantom, lesions, rotation_params, translation_params):
    """
    Takes as input phantom and lesions generated from create_phantom_... and applies known rotation and translation in sitk
    
    Parameters
    ----------
    phantom : SimpleITK.Image
        The original phantom image.
    lesions : list of SimpleITK cordinates in 3D
        List of lesion points in the original phantom coordinate system.
    rotation_params : tuple
        Parameters for rotation transformation.
    translation_params : tuple
        Parameters for translation transformation.

    Returns
    -------
    transformed_phantom : SimpleITK.Image
        The transformed phantom image.
    transformed_lesions : list of SimpleITK cooridnates in 3D
        List of transformed lesion points.
    known_transformation : SimpleITK.CompositeTransform
        The known composite transformation applied to the phantom and lesions.
        Composite transformations are applied in stack order.

    """
    # Define rotation transformation
    rotation = sitk.Euler3DTransform()
    rotation.SetRotation(*rotation_params)
    
    # Define translation transformation
    translation = sitk.TranslationTransform(3)
    translation.SetOffset(translation_params)
    
    # Combine transformations into composite transform
    composite_transform = sitk.CompositeTransform([translation, rotation])
    
    # Apply transformation to phantom
    transformed_phantom = sitk.Resample(phantom, phantom.GetSize(), composite_transform, sitk.sitkLinear,
                                        phantom.GetOrigin(), phantom.GetSpacing(), phantom.GetDirection(),
                                        0.0, phantom.GetPixelID())
    
    # Apply rotation to the phantom to create visualization of moving image
    transformed_phantom_1 = sitk.Resample(phantom, phantom.GetSize(), rotation, sitk.sitkLinear,
                                        phantom.GetOrigin(), phantom.GetSpacing(), phantom.GetDirection(),
                                        0.0, phantom.GetPixelID())
    
    # Apply translation to the transformed phantom to create visualization of moving image
    transformed_phantom_1 = sitk.Resample(transformed_phantom_1, transformed_phantom_1.GetSize(), translation,
                                        sitk.sitkLinear, transformed_phantom_1.GetOrigin(),
                                        transformed_phantom_1.GetSpacing(), transformed_phantom_1.GetDirection(),
                                        0.0, transformed_phantom_1.GetPixelID())
    
    
    # Apply transformation to lesions to obtain the moving coordinates
    transformed_lesions = [composite_transform.TransformPoint(p) for p in lesions]
    
    
    # Apply transformation to lesions for visualization
    rotation_1, translation_1 = generate_visualization_composite_transform(rotation_params, translation_params)
    
    transformed_lesions_1 = [rotation_1.TransformPoint(p) for p in lesions]
    transformed_lesions_1 = [translation_1.TransformPoint(p) for p in transformed_lesions_1]
    
    return transformed_phantom, transformed_lesions, transformed_lesions_1, transformed_phantom_1
