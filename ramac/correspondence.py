# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 21:21:29 2024

@author: Qian.Cao
"""

import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment

def hungarian(points_0, points_1, threshold):
    """
    Implements Hungarian algorithm. Finds corresponding points in points_0 and points_1

    """

    # correspondences
    correspondences = []

    # compute distances between two point clouds
    distances = cdist(points_0, points_1)
    row_ind, col_ind = linear_sum_assignment(distances)

    # compute matched points
    for i, j in zip(row_ind, col_ind):
        distance = distances[i, j]
        if distance <= threshold:
            match_status = 'matched'

            # save to correspondences
            correspondences.append(i,j)
        else:
            match_status = 'not matched'

    return correspondences