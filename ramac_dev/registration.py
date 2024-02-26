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
    """
    Perform registration of fixed and moving images, returns resulting transformation.

    Parameters
    ----------
    fixed : sitk.Image
        DESCRIPTION.
    moving : sitk.Image
        DESCRIPTION.

    Returns
    -------
    outTx : TYPE
        DESCRIPTION.

    """
    
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

def transform_image(moving: sitk.Image, fixed: sitk.Image, transform: sitk.Transform) -> sitk.Image:
    """
    Transform moving image according to input transform, needs fixed image as the reference image.

    Parameters
    ----------
    moving : sitk.Image
        DESCRIPTION.
    transform : sitk.Transform
        DESCRIPTION.

    Returns
    -------
    Resampeld moving image: sitk.Image

    """
    
    # Create resampler
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixed)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(0)
    resampler.SetTransform(transform)
    
    # Resampled image
    out = resampler.Execute(moving)
    
    return out

def transform_point(point: tuple, transform: sitk.Transform):
    """
    Transform a point in physical coordinates using sitk.Transform, returns transformed point in physical coordinates
    """
    
    transformed_point = transform.TransformPoint(point)
    
    return transformed_point