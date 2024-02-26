# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 20:17:08 2024

@author: Qian.Cao
"""

import numpy as np
import SimpleITK as sitk
from phantominator import shepp_logan
from ..ramac.utils import *

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
    
    # lesion coordinates
    lesion_coords = [(50, 64, 100), (80, 64, 20)]
    lesion_radii = [3, 8]
    lesion_intensity = [0.5, 1]
    
    for ind, lesions in enumerate(lesion_coords):
        phantom = insert_sphere_in_numpy_array(phantom,lesion_coords[ind],lesion_radii[ind])
        
    