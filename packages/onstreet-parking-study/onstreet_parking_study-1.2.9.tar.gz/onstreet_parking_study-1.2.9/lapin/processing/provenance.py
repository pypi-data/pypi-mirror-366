""" Preprocessing for Origin Destination data
"""

import numpy as np
import pandas as pd
from geopy.distance import geodesic


def get_immo_origins(plaques_data, distance=True) -> pd.DataFrame:
    """Add columns ori_lat, ori_lng and dist_ori_m to data. Those
    columns correspond to infered origin of the vehicules sighted.

    Parameters
    ----------
    plaques_data: pd.DataFrame.
        Correspondance between immatricualtion plaque and postal codes.
    distance : boolean (Default: True).
        Indicates if the trip distance is to be computed.

    Returns
    -------
    data : pd.DataFrame
        Enhancer data with columns ori_lat, ori_lng and dist_ori_m added.
    """

    def distance_point(lat_x, lng_x, lat_y, lng_y):
        if np.isnan(lat_x) or np.isnan(lng_x):
            return -1
        if np.isnan(lat_y) or np.isnan(lng_y):
            return -1

        return geodesic((lng_x, lat_x), (lng_y, lat_y)).m

    data = plaques_data.copy()

    # distance
    if distance:
        data["dist_ori_m"] = data.apply(
            lambda x: distance_point(x.dest_lat, x.dest_lng, x.ori_lat, x.ori_lng),
            axis=1,
        )

        return data
