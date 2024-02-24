# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 13:45:03 2024

Utility functions for reading dicom, converting formats, etc.

@author: Qian.Cao
"""

import numpy as np
import SimpleITK as sitk

def array_to_sitk(x,spacing=(1.,)*3,origin=(0.,)*3):
    """
    
    
    
    """
    
    x_sitk = sitk.GetImageFromArray(x)
    x_sitk.SetOrigin(origin)
    x_sitk.SetSpacing(spacing)
    
    return x_sitk