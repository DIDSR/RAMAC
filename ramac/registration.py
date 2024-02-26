# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 12:39:23 2024

Tools for image registration.

@author: Qian.Cao
"""

import numpy as np
import SimpleITK as sitk

def _setup_rigid_registration():
    """

    Creates a simple registration object with metric, optimizer and interpolator

    Returns
    -------
    R : sitk.ImageRegistrationMethod
        Parameters for Rigid Registration

    """
    
    R = sitk.ImageRegistrationMethod()
    R.SetMetricAsCorrelation()
    R.SetOptimizerAsRegularStepGradientDescent(
        learningRate=2.0,
        minStep=1e-4,
        numberOfIterations=500,
        gradientMagnitudeTolerance=1e-8,
    )
    R.SetOptimizerScalesFromIndexShift()
    R.SetInterpolator(sitk.sitkLinear)
    
    return R

def register_image(fixed: sitk.Image,
                   moving: sitk.Image) -> sitk.Transform:
    
    # Set up rigid registration parameters
    R = _setup_rigid_registration()
    
    # Set up initial transform
    tx = sitk.CenteredTransformInitializer(
        fixed, moving, sitk.Similarity3DTransform()
    )
    R.SetInitialTransform(tx)
    
    # add command
    # R.AddCommand(sitk.sitkIterationEvent, lambda: command_iteration(R))
    
    # run registration
    outTx = R.Execute(fixed, moving)
    
    return outTx

def transform_image(moving, transform):
    
    pass

def transform_point(point, transform):
    
    pass