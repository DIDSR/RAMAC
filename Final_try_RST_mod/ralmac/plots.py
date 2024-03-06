#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import matplotlib.pyplot as plt
import numpy as np
import SimpleITK as sitk
from mpl_toolkits.mplot3d import Axes3D
from ipywidgets import interact, IntSlider, fixed

import matplotlib.pyplot as plt
import numpy as np
import SimpleITK as sitk
from ipywidgets import interact, IntSlider, fixed

def plot_slices_interactive(image, slice_x, slice_y, slice_z):
    """
    Plot interactive slices along each axis of the provided image.

    Args:
        image (SimpleITK.Image): The input 3D image.
        slice_x (int): The slice index along the x-axis.
        slice_y (int): The slice index along the y-axis.
        slice_z (int): The slice index along the z-axis.

    Returns:
        None
    """
    # Plot slices along each axis
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    
    # Plot slices along the x-axis
    axs[0].imshow(np.flipud(sitk.GetArrayViewFromImage(image[slice_x, :, :]).T), cmap='gray')
    axs[0].set_title('X-axis Slice')

    # Plot slices along the y-axis
    axs[1].imshow(np.flipud(sitk.GetArrayViewFromImage(image[:, slice_y, :]).T), cmap='gray')
    axs[1].set_title('Y-axis Slice')

    # Plot slices along the z-axis
    axs[2].imshow(np.flipud(sitk.GetArrayViewFromImage(image[:, :, slice_z]).T), cmap='gray')
    axs[2].set_title('Z-axis Slice')

    plt.show()

def compare_slices_interactive(original_phantom, transformed_phantom, moving_resampled):
    """
    Compare slices interactively for three input images.

    Args:
        original_phantom (SimpleITK.Image): The original phantom image.
        transformed_phantom (SimpleITK.Image): The transformed phantom image (which is the moving image).
        moving_resampled (SimpleITK.Image): The resampled moving image (registered image).

    Returns:
        None
    """
    # Define slice indices
    image_size = original_phantom.GetSize()
    max_x, max_y, max_z = image_size[0]-1, image_size[1]-1, image_size[2]-1

    # Create interactive visualization for original phantom
    interact(
        plot_slices_interactive,
        image=fixed(original_phantom),
        slice_x=IntSlider(min=0, max=max_x, step=1, value=int(max_x/2)),
        slice_y=IntSlider(min=0, max=max_y, step=1, value=int(max_y/2)),
        slice_z=IntSlider(min=0, max=max_z, step=1, value=int(max_z/2))
    )
    
    # Define slice indices
    image_size = transformed_phantom.GetSize()
    max_x, max_y, max_z = image_size[0]-1, image_size[1]-1, image_size[2]-1

    # Create interactive visualization for transformed phantom
    interact(
        plot_slices_interactive,
        image=fixed(transformed_phantom),
        slice_x=IntSlider(min=0, max=max_x, step=1, value=int(max_x/2)),
        slice_y=IntSlider(min=0, max=max_y, step=1, value=int(max_y/2)),
        slice_z=IntSlider(min=0, max=max_z, step=1, value=int(max_z/2))
    )
    
    # Define slice indices
    image_size = moving_resampled.GetSize()
    max_x, max_y, max_z = image_size[0]-1, image_size[1]-1, image_size[2]-1

    # Create interactive visualization for moving resampled image
    interact(
        plot_slices_interactive,
        image=fixed(moving_resampled),
        slice_x=IntSlider(min=0, max=max_x, step=1, value=int(max_x/2)),
        slice_y=IntSlider(min=0, max=max_y, step=1, value=int(max_y/2)),
        slice_z=IntSlider(min=0, max=max_z, step=1, value=int(max_z/2))
    )



def plot_lesions(original_phantom, transformed_phantom, moving_resampled, fixed_voxel_tuples, transformed_lesions_rounded, registered_voxel_tuples):
    """
    Plots visualizations of lesions on different slices of the obtained images (fixed, moving and registered).

    Args:
        original_phantom (SimpleITK.Image): The original phantom image.
        transformed_phantom (SimpleITK.Image): The transformed phantom image.
        moving_resampled (SimpleITK.Image): The resampled moving image.
        fixed_voxel_tuples (list): List of tuples containing voxel coordinates of lesions in the fixed image.
        transformed_lesions_rounded (list): List of tuples containing transformed lesion coordinates for visualization.
        registered_voxel_tuples (list): List of tuples containing voxel coordinates of lesions in the registered image.

    Returns:
        None
    """
    num_lesions = len(fixed_voxel_tuples)
    num_rows = 3 * num_lesions
    num_cols = 3

    plt.figure(figsize=(15, 5*num_rows))

    # Initialize subplot index
    subplot_index = 1

    for lesion_num in range(num_lesions):
        fixed_coords = fixed_voxel_tuples[lesion_num]
        transformed_coords = transformed_lesions_rounded[lesion_num]
        registered_coords = registered_voxel_tuples[lesion_num]

        # Set suptitle for each lesion
        plt.suptitle("Lesion Visualization", fontsize=16, fontweight='bold', x=0.5, y=1.00)
        
        # Plot X slice
        slice_index = fixed_coords[0]
        plt.subplot(num_rows, num_cols, subplot_index)
        plt.imshow(np.flipud(sitk.GetArrayFromImage(original_phantom)[slice_index, :, :].T), cmap="gray")
        plt.scatter(fixed_coords[1], original_phantom.GetSize()[2] - fixed_coords[2], color='red', label='Lesion Coordinates')
        plt.title("Fixed_Image - X slice")
        plt.axis("off")
        subplot_index += 1

        slice_index_r = transformed_coords[0]
        plt.subplot(num_rows, num_cols, subplot_index)
        plt.imshow(np.flipud(sitk.GetArrayFromImage(transformed_phantom)[slice_index_r, :, :].T), cmap="gray")
        plt.scatter(transformed_coords[1], transformed_phantom.GetSize()[2] - transformed_coords[2], color='red',label='Lesion Coordinates')
        plt.title("Transformed_Image - X slice")
        plt.axis("off")
        subplot_index += 1

        slice_index_m = registered_coords[0]
        plt.subplot(num_rows, num_cols, subplot_index)
        plt.imshow(np.flipud(sitk.GetArrayFromImage(moving_resampled)[slice_index_m, :, :].T), cmap="gray")
        plt.scatter(registered_coords[1], moving_resampled.GetSize()[2] - registered_coords[2], color='red', label='Lesion Coordinates')
        plt.title("Moving_Resampled_Image - X slice")
        plt.axis("off")
        subplot_index += 1

        # Plot Y slice
        slice_index = fixed_coords[1]
        plt.subplot(num_rows, num_cols, subplot_index)
        plt.imshow(np.flipud(sitk.GetArrayFromImage(original_phantom)[:, slice_index, :].T), cmap="gray")
        plt.scatter(fixed_coords[0], original_phantom.GetSize()[2] - fixed_coords[2], color='red', label='Lesion Coordinates')
        plt.title("Fixed_Image - Y slice")
        plt.axis("off")
        subplot_index += 1

        slice_index_r = transformed_coords[1]
        plt.subplot(num_rows, num_cols, subplot_index)
        plt.imshow(np.flipud(sitk.GetArrayFromImage(transformed_phantom)[:, slice_index_r, :].T), cmap="gray")
        plt.scatter(transformed_coords[0], transformed_phantom.GetSize()[2] - transformed_coords[2], color='red',label='Lesion Coordinates')
        plt.title("Transformed_Image - Y slice")
        plt.axis("off")
        subplot_index += 1

        slice_index_m = registered_coords[1]
        plt.subplot(num_rows, num_cols, subplot_index)
        plt.imshow(np.flipud(sitk.GetArrayFromImage(moving_resampled)[:, slice_index_m, :].T), cmap="gray")
        plt.scatter(registered_coords[0], moving_resampled.GetSize()[2] - registered_coords[2], color='red', label='Lesion Coordinates')
        plt.title("Moving_Resampled_Image - Y slice")
        plt.axis("off")
        subplot_index += 1

        # Plot Z slice
        slice_index = fixed_coords[2]
        plt.subplot(num_rows, num_cols, subplot_index)
        plt.imshow(np.flipud(sitk.GetArrayFromImage(original_phantom)[:, :, slice_index].T), cmap="gray")
        plt.scatter(fixed_coords[0], original_phantom.GetSize()[1] - fixed_coords[1], color='red', label='Lesion Coordinates')
        plt.title("Fixed_Image - Z slice")
        plt.axis("off")
        subplot_index += 1

        slice_index_r = transformed_coords[2]
        plt.subplot(num_rows, num_cols, subplot_index)
        plt.imshow(np.flipud(sitk.GetArrayFromImage(transformed_phantom)[:, :, slice_index_r].T), cmap="gray")
        plt.scatter(transformed_coords[0], transformed_phantom.GetSize()[1] - transformed_coords[1], color='red',label='Lesion Coordinates')
        plt.title("Transformed_Image - Z slice")
        plt.axis("off")
        subplot_index += 1

        slice_index_m = registered_coords[2]
        plt.subplot(num_rows, num_cols, subplot_index)
        plt.imshow(np.flipud(sitk.GetArrayFromImage(moving_resampled)[:, :, slice_index_m].T), cmap="gray")
        plt.scatter(registered_coords[0], moving_resampled.GetSize()[1] - registered_coords[1], color='red', label='Lesion Coordinates')
        plt.title("Moving_Resampled_Image - Z slice")
        plt.axis("off")
        subplot_index += 1

    # Adjust layout to eliminate gaps between rows
    plt.tight_layout(pad=0.1)
    plt.show()

def ordinal(n):
    """
    Converts a number into its ordinal representation.

    Args:
        n (int): The number to be converted.

    Returns:
        str: The ordinal representation of the number.
    """
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return f"{n}{suffix}"



