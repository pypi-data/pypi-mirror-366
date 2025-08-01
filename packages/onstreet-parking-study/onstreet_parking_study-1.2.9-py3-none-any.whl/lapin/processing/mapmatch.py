""" Match data
"""
import logging

import numpy as np
import pandas as pd
import geopandas as gpd

from lapin import constants
from lapin.processing.matcher import MapMatcher
from lapin.tools.geom import rtreenearest
from lapin.constants import (
    MONTREAL_CRS,
    DEFAULT_CRS
)
from lapin.core import TrajDataFrame

logger = logging.getLogger(__name__)


def mapmatch(
    veh_data: TrajDataFrame,
    matcher: MapMatcher,
    timestamp: bool = False
) -> TrajDataFrame:
    """ Return and updadte data with collected points matched onto the road.

    Parameters
    ----------
    host: str
        The url for the OSRM host.
    return_edge: boolean (Default: False)
        Return OSRM edge where points have matched.

    Returns
    -------
    data: pandas.DataFrame
        Data with matched point onto the roads. Addd columns 'lat_matched'
        and 'lng_matched'.
    """
    data = veh_data.copy()

    if 'lat_match' in veh_data.columns or 'lng_match' in veh_data.columns:
        return data

    data['day'] = data[constants.DATETIME].dt.date

    # mapmatching
    # iterate over each trip from each day
    df = pd.DataFrame()
    groups = data.groupby([constants.UUID, 'day'])

    for (trip_id, date), data_trips in groups:
        logger.info('treating vehicule %s on day %s', trip_id, date)
        data_trips = data_trips.sort_values('datetime')
        coords = data_trips[['lat', 'lng']].dropna().values
        if coords.shape[0] <= 1:
            continue

        # matching
        if timestamp:
            timestamps = (
                data_trips[constants.DATETIME].astype('int64') //
                10**9
            ).values
            data_enanced = matcher.match(coords, timestamps=timestamps)
        else:
            data_enanced = matcher.match(coords)

        data_enanced['data_index'] = data_trips.index.values
        # concat
        df = pd.concat([df, data_enanced])
        # edge_index received from valhalla seem to overflow, which means that instead of a normal int, we receive a value of 18446744073709551615
        # in some rare cases, this will crash the to_sql method when it types it as a uint64
        # forcing large edge_index into NaNs prevents crash. largest values ever received from valhalla was ~3000
        # using a large margin of security (4 fold), any value larger than 30 000 000 will be converted to NaN (and null once stored in the db)
        # references to this issue :
        # https://github.com/valhalla/valhalla/issues/3626
        # https://github.com/valhalla/valhalla/issues/3699
        # https://github.com/valhalla/valhalla/pull/4911
        df.loc[df.edge_index > 30000000, 'edge_index'] = np.nan

    # drop day column
    data.drop(columns='day', inplace=True)

    # enhancing data
    df = df.set_index('data_index')
    data = pd.concat([data, df], axis=1)

    return data


def valhalla_mapmatch(
    veh_data: TrajDataFrame,
    matcher: MapMatcher,
    roads: gpd.GeoDataFrame,
    timestamp: bool = False
) -> TrajDataFrame:
    """Return and updadte data with collected points matched onto the road.

    Parameters
    ----------
    host: str
        The url for the OSRM host.
    return_edge: boolean (Default: False)
        Return OSRM edge where points have matched.

    Returns
    -------
    data: pandas.DataFrame
        Data with matched point onto the roads. Addd columns 'lat_matched'
        and 'lng_matched'.
    """
    param = veh_data.parameters
    crs = veh_data.crs

    data = mapmatch(veh_data, matcher, timestamp)
    data = data.drop(columns='geometry')
    data = matcher.post_process_matching(data, roads)

    data = TrajDataFrame(data, parameters=param, crs=crs)

    return data


def match_custom_roadnetwork(
    data: TrajDataFrame,
    roads: gpd.GeoDataFrame,
    roads_id_col: str = 'ID_TRC',
    mapmatching: bool = True
) -> TrajDataFrame:
    """_summary_

    Parameters
    ----------
    veh_data : TrajDataFrame
        _description_
    geobase : gpd.GeoDataFrame
        _description_
    geobase_id_col : str, optional
        _description_, by default 'ID_TRC'

    Returns
    -------
    TrajDataFrame
        _description_
    """
    data = data.copy()
    lat_col = constants.LATITUDE
    lng_col = constants.LONGITUDE

    if mapmatching:
        lat_col += '_match'
        lng_col += '_match'

    parameters = data.parameters
    crs = data.crs
    data = gpd.GeoDataFrame(
        data=data,
        geometry=gpd.points_from_xy(data[lng_col], data[lat_col]),
        crs=DEFAULT_CRS
    )

    # Enforce crs matching
    roads = roads.copy().to_crs(DEFAULT_CRS)
    roads = roads.to_crs(MONTREAL_CRS)
    data = data.to_crs(MONTREAL_CRS)

    # create road matching
    data_x_roads = rtreenearest(data, roads, gdf_b_cols=[roads_id_col])

    # drop points that fall in two zones
    data_x_roads['data_index'] = data_x_roads.index
    data_x_roads_index = (
        data_x_roads.sort_values(['data_index', 'dist'])[['data_index']]
                    .drop_duplicates(keep='first')
                    .index
    )
    data_x_roads = data_x_roads[data_x_roads.index.isin(data_x_roads_index)]
    data_x_roads = data_x_roads.reset_index(drop=True)

    # drop point too far from a road
    data_x_roads.loc[data_x_roads['dist'] >= 10, roads_id_col] = np.nan

    # clean columns
    data_x_roads.rename(columns={roads_id_col: 'segment'}, inplace=True)
    data_x_roads.drop(columns=['data_index'], inplace=True)
    data_x_roads = data_x_roads.to_crs(DEFAULT_CRS)

    # convert to traj_dataFrame
    data_x_roads = data_x_roads.drop(columns='geometry')
    data_x_roads = TrajDataFrame(data_x_roads, parameters=parameters, crs=crs)

    return data_x_roads
