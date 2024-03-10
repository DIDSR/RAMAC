#!/usr/bin/env python
# coding: utf-8

# In[6]:

import pandas as pd
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment
import matplotlib.pyplot as plt

def read_lesion_csv(file_path):
    """
    Read a CSV file containing lesion data into a DataFrame.

    Parameters:
        file_path (str): The file path to the CSV file.

    Returns:
        pandas.DataFrame: A DataFrame containing the lesion data.
    """
    # Define column names
    column_names = ['x', 'y', 'z', 'Index']
    
    # Read CSV into DataFrame
    df = pd.read_csv(file_path, names=column_names, header=0, dtype={'Index': str})
    
    return df


def find_corresponding_lesions_timepoints(df1_file, df2_file, threshold):
    """
    Find corresponding lesions between two sets of lesions or ROIs.

    Parameters:
        df1_file (str): The file path to the first set of lesions or ROIs.
        df2_file (str): The file path to the second set of lesions or ROIs.
        threshold (float): The threshold distance for considering lesions or ROIs as corresponding.

    Returns:
        Tuple[pandas.DataFrame, pandas.DataFrame, pandas.DataFrame]: 
        A tuple containing correspondences DataFrame, unmatched indices DataFrame from the first file,
        and unmatched indices DataFrame from the second file.
    """
    # Read CSV files into DataFrames
    df1 = read_lesion_csv(df1_file)
    df2 = read_lesion_csv(df2_file)

    # Initialize the correspondence data frame with 'F_I' and 'R_I' columns
    correspondences = pd.DataFrame(columns=['F_I', 'Fixed_Index', 'R_I', 'Reg_Index', 'Distance', 'Match_Status'])

    # Function to process each group
    def process_group(df1_group, df2_group, threshold):
        nonlocal correspondences
        if not df1_group.empty and not df2_group.empty:
            distances = cdist(df1_group[['x', 'y', 'z']].values, df2_group[['x', 'y', 'z']].values)
            row_ind, col_ind = linear_sum_assignment(distances)
            for i, j in zip(row_ind, col_ind):
                distance = distances[i, j]
                if distance <= threshold:
                    match_status = 'matched'
                else:
                    match_status = 'not matched'
                # Append the match information including 'F_I' and 'R_I'
                correspondences = pd.concat([correspondences, pd.DataFrame({
                    'F_I': [df1_group.index[i]],
                    'Fixed_Index': [df1_group.iloc[i]['Index']],
                    'R_I': [df2_group.index[j]],
                    'Reg_Index': [df2_group.iloc[j]['Index']],
                    'Distance': [distance],
                    'Match_Status': [match_status]
                })], ignore_index=True)

    # Process lesions if there are common lesions
    if not df1.empty and not df2.empty:
        process_group(df1, df2, threshold)
    
    # Handle unmatched lesions
    unmatched_df1_index = set(df1['Index']) - set(correspondences['Fixed_Index'])
    unmatched_df2_index = set(df2['Index']) - set(correspondences['Reg_Index'])

    # Create DataFrames for unmatched index
    unmatched_index_df1 = pd.DataFrame({'Fixed_Index': list(unmatched_df1_index), 'UnMatch': 'No correspondence found'})
    unmatched_index_df2 = pd.DataFrame({'Reg_Index': list(unmatched_df2_index), 'UnMatch': 'No correspondence found'})
    
    # Now, process 'not matched' entries by Hard Thresholding
    not_matched_by_hdt_df1 = correspondences[correspondences['Match_Status'] == 'not matched']['Fixed_Index']
    not_matched_by_hdt_df2 = correspondences[correspondences['Match_Status'] == 'not matched']['Reg_Index']
    
    # Append 'not matched' by hard thresholding to the unmatched DataFrames
    unmatched_index_df1 = pd.concat([unmatched_index_df1, pd.DataFrame({
        'Fixed_Index': not_matched_by_hdt_df1, 
        'UnMatch': 'By Hungarian distance and Thresholding'
    })], ignore_index=True)

    unmatched_index_df2 = pd.concat([unmatched_index_df2, pd.DataFrame({
        'Reg_Index': not_matched_by_hdt_df2, 
        'UnMatch': 'By Hungarian distance and Thresholding'
    })], ignore_index=True)

    return correspondences, unmatched_index_df1, unmatched_index_df2

def process_lesion_timepoints(screening_file, transformed_file, threshold):
    correspondences, unmatched_names_df1, unmatched_names_df2 = find_corresponding_lesions_timepoints(
        screening_file, transformed_file, threshold
    )

    # Return the results
    return correspondences, unmatched_names_df1, unmatched_names_df2

def plot_lesion_correspondences_timepoints(df1_file, df2_file):
    """
    Plot lesion correspondences between two timepoints.

    Parameters:
        df1_file (str): The file path to the first set of lesions or ROIs.
        df2_file (str): The file path to the second set of lesions or ROIs.
    """
    # Calculate correspondences and unmatched names
    correspondences, unmatched_names_df1, unmatched_names_df2 = find_corresponding_lesions_timepoints(df1_file, df2_file, threshold=30)
    df1 = read_lesion_csv(df1_file)
    df2 = read_lesion_csv(df2_file)

    # Plot the lesions and their correspondences
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Helper function to plot a check or cross
    def plot_check_or_cross(ax, mid_point, status):
        if status == 'matched':
            ax.text(*mid_point, '✓', color='green', fontsize=12, ha='center', va='center')
        elif status == 'not matched':
            ax.text(*mid_point, '✗', color='red', fontsize=12, ha='center', va='center')

    # Plot lesions from df1
    for index, row in df1.iterrows():
        ax.scatter(row['x'], row['y'], row['z'], color='blue', s=50, label='Fixed_Coordinates' if index == 0 else "", alpha=0.6)
        ax.text(row['x'], row['y'], row['z'], row['Index'], color='blue')

    # Plot lesions from df2
    for index, row in df2.iterrows():
        ax.scatter(row['x'], row['y'], row['z'], color='red', s=50, label='Registered_Coordinates' if index == 0 else "", alpha=0.6)
        ax.text(row['x'], row['y'], row['z'], row['Index'], color='red')

    # Draw lines between corresponding lesions and annotate distances
    for index, row in correspondences.iterrows():
        lesion1 = df1.iloc[row['F_I']]
        lesion2 = df2.iloc[row['R_I']]
        # Plot the connecting line
        ax.plot([lesion1['x'], lesion2['x']], [lesion1['y'], lesion2['y']], [lesion1['z'], lesion2['z']],
                'gray', linestyle='--', marker='')
        # Calculate the midpoint of the line
        mid_point = ((lesion1['x'] + lesion2['x']) / 2, (lesion1['y'] + lesion2['y']) / 2, (lesion1['z'] + lesion2['z']) / 2)
        # Annotate the distance at the midpoint
        distance_text = f"{row['Distance']:.2f}"
        ax.text(*mid_point, distance_text, color='black')

        # Plot check or cross based on Match_Status
        plot_check_or_cross(ax, mid_point, row['Match_Status'])

    # Set legend and labels
    ax.legend()
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.title('Lesion Correspondences Between Radiologists')
    plt.show()

def create_final_dataframe_timepoints(correspondences, unmatched_names_df1, unmatched_names_df2, df1_file, df2_file):
    """
    Create a final DataFrame containing lesion correspondences between two timepoints.

    Parameters:
        correspondences (pandas.DataFrame): DataFrame containing lesion or ROI correspondences.
        unmatched_names_df1 (pandas.DataFrame): DataFrame containing unmatched indices from the first file.
        unmatched_names_df2 (pandas.DataFrame): DataFrame containing unmatched indices from the second file.
        df1_file (str): The file path to the first set of lesions or ROIs.
        df2_file (str): The file path to the second set of lesions or ROIs.

    Returns:
        pandas.DataFrame: A DataFrame containing the final lesion correspondences.
    """
    # Read CSV files into DataFrames
    df1 = read_lesion_csv(df1_file)
    df2 = read_lesion_csv(df2_file)
    
    # Initialize a list to collect dictionaries
    data = []

    # Process 'matched' correspondences
    matched_correspondences = correspondences[correspondences['Match_Status'] == 'matched']
    for _, row in matched_correspondences.iterrows():
        updated_index = row['Fixed_Index']
        fixed_index = row['Fixed_Index']
        reg_index = row['Reg_Index']

        # Find the Fixed Centroid from df1
        fixed_centroid = df1.loc[df1['Index'] == fixed_index, ['x', 'y', 'z']].values[0]

        # Find the Reg Centroid from df2
        reg_centroid = df2.loc[df2['Index'] == reg_index, ['x', 'y', 'z']].values[0]

        # Merge Centroid is the same as Reg Centroid
        merge_centroid = reg_centroid.tolist()

        data.append({
            'Updated Index': str(int(updated_index)) if updated_index == int(updated_index) else updated_index,
            'Fixed Index': str(int(fixed_index)) if fixed_index == int(fixed_index) else fixed_index,
            'Fixed Centroid': fixed_centroid.tolist(),
            'Reg Index': str(int(reg_index)) if reg_index == int(reg_index) else reg_index,
            'Reg Centroid': reg_centroid.tolist(),
            'Merge Centroid': merge_centroid
        })

    # Process 'Not matched' entries in unmatched_names_df1
    for _, row in unmatched_names_df1.iterrows():
        fixed_index = row['Fixed_Index']

        # Find the Fixed Centroid from df1
        fixed_centroid = df1.loc[df1['Index'] == fixed_index, ['x', 'y', 'z']].values[0]

        # For unmatched cases, Reg Index and Reg Centroid are 'Not matched'
        reg_index = 'Not matched'
        reg_centroid = 'Not matched'

        # Merge Centroid is the same as Fixed Centroid in those cases
        merge_centroid = fixed_centroid.tolist()

        data.append({
            'Updated Index': str(int(fixed_index)) if fixed_index == int(fixed_index) else fixed_index,
            'Fixed Index': str(int(fixed_index)) if fixed_index == int(fixed_index) else fixed_index,
            'Fixed Centroid': fixed_centroid.tolist(),
            'Reg Index': reg_index,
            'Reg Centroid': reg_centroid,
            'Merge Centroid': merge_centroid
        })

    # Process 'Not matched' entries in unmatched_names_df2
    max_updated_index = int(correspondences['Fixed_Index'].max()) if not correspondences.empty else 0
    for _, row in unmatched_names_df2.iterrows():
        reg_index = row['Reg_Index']
        max_updated_index += 1  # Increment the updated index

        # Find the Reg Centroid from df2
        reg_centroid = df2.loc[df2['Index'] == reg_index, ['x', 'y', 'z']].values[0]

        # For unmatched cases, Fixed Index and Fixed Centroid are 'Not matched'
        fixed_index = 'Not matched'
        fixed_centroid = 'Not matched'

        # Merge Centroid is the same as Reg Centroid in those cases
        merge_centroid = reg_centroid.tolist()

        data.append({
            'Updated Index': str(max_updated_index),
            'Fixed Index': fixed_index,
            'Fixed Centroid': fixed_centroid,
            'Reg Index': str(int(reg_index)) if reg_index == int(reg_index) else reg_index,
            'Reg Centroid': reg_centroid.tolist(),
            'Merge Centroid': merge_centroid
        })

    # Convert the list of dictionaries into a DataFrame
    new_df = pd.DataFrame(data)

    return new_df
