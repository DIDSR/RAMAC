# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 20:17:08 2024

@author: Qian.Cao
"""

import numpy as np
import SimpleITK as sitk
from phantominator import shepp_logan
import matplotlib.pyplot as plt

# TODO: fix to use relative imports
import sys
sys.path.append("../ramac")
from utils import numpy_array_to_sitk, numpy_points_to_sitk

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
    spacing = (0.5,)*3
    origin = (0.,)*3
    
    # create shepp logan test phantom
    phantom = shepp_logan(phantom_shape)
    
    # lesion parameters
    lesion_coords = [(50, 64, 100), (80, 64, 20)]
    lesion_radii = [3, 8]
    lesion_intensity = [0.5, 1]
    
    # inserts lesion
    for ind, lesions in enumerate(lesion_coords):
        phantom = insert_sphere_in_numpy_array(phantom,lesion_coords[ind],lesion_radii[ind],lesion_intensity[ind])
        
    phantom = numpy_array_to_sitk(phantom,spacing=spacing,origin=origin)
    lesions = numpy_points_to_sitk(lesion_coords,phantom)
        
    return phantom, lesions

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

def view_phantom(phantom: sitk.Image, title=None):
    """
    Display sitk image

    Parameters
    ----------
    phantom : sitk.Image
        DESCRIPTION.

    Returns
    -------
    plot : TYPE
        DESCRIPTION.

    """
    
    plot = plt.imshow(sitk.GetArrayFromImage(phantom)[phantom.GetSize()[2] // 2,:,:], cmap='gray')
    plt.title(title)
    plt.axis('off')
    plt.show()
    
    return plot

if __name__ == "__main__":
    
    phantom, lesions = create_phantom_shepplogan()
    
    view_phantom(phantom)