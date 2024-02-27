#!/usr/bin/env python
# coding: utf-8

# In[5]:


import os
import numpy as np
import SimpleITK as sitk
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
from ipywidgets import interact, fixed
from IPython.display import clear_output


def display_images(fixed_image_z, moving_image_z, fixed_npa, moving_npa):
    """
    Display images from the fixed and moving image stacks.
    
    Parameters:
        fixed_image_z (int): The index of the slice to be displayed from the fixed image stack.
        moving_image_z (int): The index of the slice to be displayed from the moving image stack.
        fixed_npa (numpy.ndarray): The numpy array representing the fixed image stack.
        moving_npa (numpy.ndarray): The numpy array representing the moving image stack.
    """
    # Create a figure with two subplots and the specified size.
    plt.subplots(1,2,figsize=(10,8))
    
    # Draw the fixed image in the first subplot.
    plt.subplot(1,2,1)
    plt.imshow(fixed_npa[fixed_image_z,:,:],cmap=plt.cm.Greys_r);
    plt.title('fixed image')
    plt.axis('off')
    
    # Draw the moving image in the second subplot.
    plt.subplot(1,2,2)
    plt.imshow(moving_npa[moving_image_z,:,:],cmap=plt.cm.Greys_r);
    plt.title('moving image')
    plt.axis('off')
    
    plt.show()
    

def display_images_with_alpha(image_z, alpha, fixed, moving):
    """
    Display images with alpha blending between fixed and moving images.
    
    Parameters:
        image_z (int): The index of the slice to be displayed.
        alpha (float): The alpha blending parameter.
        fixed (SimpleITK.Image): The fixed image.
        moving (SimpleITK.Image): The moving image.
    """
    img = (1.0 - alpha)*fixed[:,:,image_z] + alpha*moving[:,:,image_z] 
    plt.imshow(sitk.GetArrayViewFromImage(img),cmap=plt.cm.Greys_r);
    plt.axis('off')
    plt.show()


def start_plot():
    """Callback invoked when the StartEvent happens, sets up our new data."""
    global metric_values, multires_iterations
    
    metric_values = []
    multires_iterations = []


def end_plot():
    """Callback invoked when the EndEvent happens, do cleanup of data and figure."""
    global metric_values, multires_iterations
    
    del metric_values
    del multires_iterations
    # Close figure, we don't want to get a duplicate of the plot latter on.
    plt.close()


def plot_values(registration_method):
    """
    Callback invoked when the IterationEvent happens, update our data and display new figure.
    
    Parameters:
        registration_method: The registration method.
    """
    global metric_values, multires_iterations
    
    metric_values.append(registration_method.GetMetricValue())                                       
    # Clear the output area (wait=True, to reduce flickering), and plot current data
    clear_output(wait=True)
    # Plot the similarity metric values
    plt.plot(metric_values, 'r')
    plt.plot(multires_iterations, [metric_values[index] for index in multires_iterations], 'b*')
    plt.xlabel('Iteration Number',fontsize=12)
    plt.ylabel('Metric Value',fontsize=12)
    plt.show()
   


# In[17]:


def update_multires_iterations():
    """Callback invoked when the sitkMultiResolutionIterationEvent happens, update the index into the metric_values list."""
    global metric_values, multires_iterations
    multires_iterations.append(len(metric_values))


def registration_3d_rigid_series (fixed_image, moving_image):
    """
    Perform 3D rigid registration between fixed and moving images.
    
    Parameters:
        fixed_image (SimpleITK.Image): The fixed image.
        moving_image (SimpleITK.Image): The moving image.
        
    Returns:
        Tuple[SimpleITK.Image, List[SimpleITK.Transform]]: 
        The resampled moving image and a list containing the initial and final transforms.
    """
    initial_transform = sitk.CenteredTransformInitializer(fixed_image, 
                                                      moving_image, 
                                                      sitk.Euler3DTransform(), 
                                                      sitk.CenteredTransformInitializerFilter.GEOMETRY)
    registration_method = sitk.ImageRegistrationMethod()

    # Similarity metric settings.
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.1)

    registration_method.SetInterpolator(sitk.sitkLinear)

    # Optimizer settings.
    registration_method.SetOptimizerAsGradientDescent(
        learningRate=0.1,
        numberOfIterations=1000,
        convergenceMinimumValue=1e-10,
        convergenceWindowSize=10,
    )
    registration_method.SetOptimizerScalesFromPhysicalShift()

    # Setup for the multi-resolution framework.
    registration_method.SetShrinkFactorsPerLevel(shrinkFactors=[2, 1, 1])
    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[4, 2, 1])
    registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

    # Don't optimize in-place, we would possibly like to run this cell multiple times.
    registration_method.SetInitialTransform(initial_transform, inPlace=False)

    # Connect all of the observers so that we can perform plotting during registration.
    registration_method.AddCommand(sitk.sitkStartEvent, start_plot)
    registration_method.AddCommand(sitk.sitkEndEvent, end_plot)
    registration_method.AddCommand(
        sitk.sitkMultiResolutionIterationEvent, update_multires_iterations
    )
    registration_method.AddCommand(
        sitk.sitkIterationEvent, lambda: plot_values(registration_method)
    )
    
    final_transform = registration_method.Execute(
    sitk.Cast(fixed_image, sitk.sitkFloat32), sitk.Cast(moving_image, sitk.sitkFloat32)
    )
    
    print(f"Final metric value: {registration_method.GetMetricValue()}")
    print(
    f"Optimizer's stopping condition, {registration_method.GetOptimizerStopConditionDescription()}"
    )
    
    moving_resampled = sitk.Resample(
    moving_image,
    fixed_image,
    final_transform,
    sitk.sitkLinear,
    0.0,
    moving_image.GetPixelID(),
    )
    
    return moving_resampled, [initial_transform, final_transform]

