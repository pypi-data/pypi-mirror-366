""" Utils
"""
import logging
from typing import List, Callable, TypeVar

import pandas as pd
import numpy as np
from jellyfish import levenshtein_distance

from lapin import constants

T = TypeVar('T')
logger = logging.getLogger(__name__)


def plates_dist(s1: str, s2: str, similarity: bool = False):
    ''' Return the Levenshtein distance between two licence plates.

    Parameters
    ----------
    s1: string
        First plate.
    s2: string
        Second plate.
    similarity: bool (Default:False)
        If true return the similarity instead of the distance.

    Returns
    -------
    dist: int.
        Distance bewteen plates
    '''
    max_dist = min(len(s1), len(s2)) + (max(len(s1), len(s2)) -
                                        min(len(s1), len(s2)))
    dist = levenshtein_distance(s1, s2)

    assert dist <= max_dist, \
        "Distance cannot be superior to the maximum distance computed."

    if similarity:
        return (max_dist - dist) / max_dist

    return dist


def pairwise(
    arr: List[T],
    distance: Callable[[T, T], float] = plates_dist,
    distance_args=None
):
    """ Construct a pairwise distance matrix for an array.

    Parameters
    ----------
    arr: List
        List of object
    distance: function
        Distance function to use
    distance_args: dict
        Optional arguments for distance function

    Return
    ------
    Matrix
        Pairwise distance matrix
    """
    if len(arr) < 2:
        return [[0]]
    if not distance_args:
        distance_args = {}
    dist_matrix = np.zeros(shape=(len(arr), len(arr)))
    for i, arr_i in enumerate(arr):
        for j, arr_j in enumerate(arr[i+1:], start=i+1):
            dist_matrix[i][j] = distance(arr_i, arr_j, **distance_args)

    for i in range(len(arr)):
        for j in range(len(arr)):
            if i == j:
                dist_matrix[i][j] = 0
            elif i > j:
                dist_matrix[i][j] = dist_matrix[j][i]

    return dist_matrix


def get_mask_avenue(
    data_enhanced: pd.DataFrame,
    roads: pd.DataFrame,
    avenue: str
) -> list[bool]:
    """ Get mask for selecting data on a specific road.

    Parameters
    ----------
    data_enhanced: pandas.DataFrame
        Data to select
    roads: pandas.DataFrame
        Mapping between road_id and road_name
    avenue: str
        Roads name

    Returns
    -------
    list[bool]
        mask
    """

    roads = roads.copy()
    data = data_enhanced.copy()

    # ID_TRC of avenue with direction of traffic = direction of digitalisation
    avenue_seg_1 = roads[
        np.logical_and(roads[constants.ROAD_NAME].str.contains(avenue),
                       roads[constants.TRAFFIC_DIR] == 1)
    ][constants.SEGMENT].unique()
    # ID_TRC of avenue with direction of traffic != direction of digitalisation
    avenue_seg_2 = roads[
        np.logical_and(roads[constants.ROAD_NAME].str.contains(avenue),
                       roads[constants.TRAFFIC_DIR] == -1)
    ][constants.SEGMENT].unique()

    # roads segments that are not in the left of Rosemont
    mask_1 = ~np.logical_and(data.segment.isin(avenue_seg_1),
                             data.side_of_street == -1)
    mask_2 = ~np.logical_and(data.segment.isin(avenue_seg_2),
                             data.side_of_street == 1)

    return mask_1 & mask_2
