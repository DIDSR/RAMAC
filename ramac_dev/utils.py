# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 13:45:03 2024

Utility functions for reading dicom, converting formats, etc.

@author: Qian.Cao
"""

import numpy as np
import pandas as pd
import SimpleITK as sitk

def numpy_array_to_sitk(x,spacing=(1.,)*3,origin=(0.,)*3):
    """
    Converts numpy array to sitk format
    
    """
    
    x_sitk = sitk.GetImageFromArray(x)
    x_sitk.SetOrigin(origin)
    x_sitk.SetSpacing(spacing)
    
    return x_sitk

def numpy_point_to_sitk(xyz, sitk_image):
    """
    Converts a numpy indices xyz to sitk point
    
    """
    
    sitk_xyz = sitk_image.TransformIndexToPhysicalPoint(xyz)
    
    return sitk_xyz

def numpy_points_to_sitk(xyzs, sitk_image):
    """
    Iteratively applies numpy_point_to_sitk to a list of coordinates

    Returns
    -------
    None.

    """
    
    sitk_xyzs = []
    
    for ind, xyz in enumerate(xyzs):
        sitk_xyzs.append(numpy_point_to_sitk(xyz, sitk_image))
        
    return sitk_xyzs

def read_lesion_csv(file_path):
    """
    Reads a csv file of point coordinates and returns them as pd.DataFrame

    Parameters
    ----------
    file_path : TYPE
        DESCRIPTION.

    Returns
    -------
    dfs : TYPE
        DESCRIPTION.

    """
    # Define column names
    column_names = ['x', 'y', 'z', 'Index']
    
    # Read CSV into DataFrame
    df = pd.read_csv(file_path, names=column_names, header=0, dtype={'Index': str})
    
    return df