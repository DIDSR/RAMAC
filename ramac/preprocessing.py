#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def mask_air(image, air_threshold=-950):
    """Mask out the air in the CT scan."""
    # Create a binary mask using thresholding
    binary_mask = image > air_threshold
    
    # Perform connected component analysis
    labeled_mask = sitk.ConnectedComponent(binary_mask)
    
    # Compute statistics of connected components
    label_sizes = sitk.LabelShapeStatisticsImageFilter()
    label_sizes.Execute(labeled_mask)
    
    # Find the label with the largest size (excluding label 0, which corresponds to background)
    largest_label = max(range(1, label_sizes.GetNumberOfLabels() + 1), key=lambda label: label_sizes.GetPhysicalSize(label))
    
    # Create a binary mask containing only the largest connected component
    largest_air_mask = labeled_mask == largest_label
    
    # Mask the original image with the largest air mask
    masked_image = sitk.Mask(image, largest_air_mask)
    
    return masked_image

