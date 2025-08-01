""" Module that does the preprocessing of Veh GPS data and LPR readings

Provides functions: enhance
"""

import os
import itertools
from typing import Tuple
import logging
import numpy as np
import pandas as pd
import geopandas as gpd

from lapin import constants
from lapin.io.load import saaq_data
from lapin.tools.utils import IncompleteDataError
from lapin.core import TrajDataFrame, LprDataFrame
from lapin.processing.cluster import park_pos_smoothing
from lapin.processing.filter import (
    denoize_plates,
    filter_by_road_network,
    filter_side_of_street_on_2_way_street,
    filter_plates,
    filter_stays,
    remove_points_far_from_road,
)
from lapin.processing.lap import compute_lpr_lap_sequences
from lapin.processing.mapmatch import (
    mapmatch,
    match_custom_roadnetwork,
    valhalla_mapmatch,
)
from lapin.processing.matcher import MapMatcher
from lapin.processing.provenance import get_immo_origins
from lapin.processing.road_network import (
    add_segment_geom,
    compute_dir_veh_for_all_detections,
    compute_veh_direction,
    get_traffic_dir,
    linear_referencing,
)

logger = logging.getLogger(__name__)


def enhance(
    lpr_data: LprDataFrame,
    veh_data: TrajDataFrame,
    roads: gpd.GeoDataFrame,
    geodouble: gpd.GeoDataFrame,
    matcher_host: str,
    save_path: str = None,
    matcher_client="valhalla",
    matcher_kwargs: dict = None,
    prov_conf: dict = None,
) -> Tuple[LprDataFrame, TrajDataFrame, pd.DataFrame, pd.DataFrame]:
    """Main function for enhancing row collected LAPI data. In sequence,
    this function:
        1. Mapmatch the collected data to the road with OSRM.
        2. Linear reference data to the geobase of Montreal.
        3. Compute logic vehicule lap through the streets.
        4. Smooth data inchorence by creating missing data and
        clustering same vehicule position.
        5. Compute the side of curb on wich each vehicule is parked.
        6. Clean doublon and unwanted streets.
        7. Compute provenance if needed.


    Parameters
    ----------
    data: pandas.DataFrame
        Raw data collected through LAPI systems.
    data_config: dict
        Configuration for the names of the mandatory columns of raw data.
    roads: geopandas.GeoDataFrame
        Data of the roads centerline. We use the geobase of Montreal in our
        project.
    roads_config: dict
        Configuration for the names of the mandatory columns of roads
        centerline.
    geodouble: geopandas.GeoDataFrame
        Data representing the curbside of the roads centerlines.
    save_path: string
        Ouptut path for the cache.
    valhalla_host: string
        URL of the OSRM engine.
    matcher_client: str, optional
        'valhalla' or 'osrm'
    prov_conf: dict, optional
        Configuration for provenance computation

    Returns
    -------
    LprDataFrame
        Enhanced dataset of the raw lpr data.
    TrajDataFrame
        Enhanced dataset of the raw position data.
    DataFrame
        Origin destination
    """
    lpr_data = lpr_data.copy()
    veh_data = veh_data.copy()
    roads = roads.copy()
    geodouble = geodouble.copy()

    if matcher_kwargs is None:
        matcher_kwargs = {}

    assert matcher_client in [
        "valhalla",
        "osrm",
    ], "Le client pour le map matching doit être un des clients spécifiés"

    matcher = MapMatcher(host=matcher_host, engine=matcher_client, **matcher_kwargs)
    # match veh parcour on geobase
    logger.info("computing matchmatching")
    if matcher.engine == "valhalla":
        veh_data = valhalla_mapmatch(veh_data, matcher, timestamp=True, roads=roads)

        lpr_data = replace_zero_position(lpr_data, veh_data)
        lpr_data = find_vehicule_wayid_for_detection(lpr_data, veh_data)

    elif matcher.engine == "osrm":
        veh_data = mapmatch(veh_data, matcher, timestamp=True)

        lpr_data = replace_zero_position(lpr_data, veh_data)
        veh_data = match_custom_roadnetwork(veh_data, roads, mapmatching=True)
        lpr_data = find_vehicule_wayid_for_detection(lpr_data, veh_data)

    # convert the side_of_car from text to int
    lpr_data["side_of_car"] = map_side_of_street(
        lpr_data["side_of_car"], {"right": 1, "left": -1}
    )
    # remove nan
    data_removed = lpr_data[lpr_data[constants.SEGMENT].isna()].copy()
    data_removed["reason"] = "segment_matched_is_nan"
    lpr_data = lpr_data[~lpr_data[constants.SEGMENT].isna()]

    null_plate = lpr_data[lpr_data[constants.PLATE].isna()]
    null_plate["reason"] = "plate_is_null"
    lpr_data = lpr_data[~lpr_data[constants.PLATE].isna()]

    # remove point outside study
    outside_study = lpr_data[
        ~lpr_data[constants.SEGMENT].isin(roads[constants.SEGMENT])
    ].copy()
    outside_study["reason"] = "segment_outside_study"
    lpr_data = lpr_data[lpr_data[constants.SEGMENT].isin(roads[constants.SEGMENT])]

    logger.info("removing points far from detected roads")
    lpr_data, far_from_road = remove_points_far_from_road(
        data=lpr_data, roads=roads, roads_id_col="segment", distance=10
    )
    far_from_road["reason"] = "distance_sup_10m_from_road"

    logger.debug(
        "%s records removed from data after mapmatching.",
        data_removed.shape[0] + outside_study.shape[0] + far_from_road.shape[0],
    )

    logger.info("computing linear_referencing")
    lpr_data = linear_referencing(lpr_data, roads, mapmatching=False)

    logger.info("computing direction of vehicules on the street")
    lpr_data = compute_dir_veh_for_all_detections(
        lpr_data, veh_data, roads, mapmatching=False
    )
    lpr_data["side_of_street"] = compute_side_of_street(
        lpr_data["side_of_car"], lpr_data["dir_veh"]
    )
    logger.info("computing lap on segments")
    lpr_data = compute_lpr_lap_sequences(lpr_data, method="segment")
    lpr_data = denoize_plates(lpr_data)
    lpr_data, plate_removed = filter_plates(lpr_data, personalized_plates=False)
    logger.info("computing smoothing of plate position on segments")
    lpr_data = park_pos_smoothing(lpr_data, delta=10, dbscan=True)
    # I personaly not endorse using this function : @antoine.laurent
    # lpr_data = lap_smoothing(lpr_data, max_lap_creation=3600)
    lpr_data, plate_other_side = filter_side_of_street_on_2_way_street(
        lpr_data, roads, constants.SEGMENT, constants.TRAFFIC_DIR
    )
    lpr_data = add_segment_geom(lpr_data, geodouble)

    plate_removed["reason"] = "plate_format_doesnt_match_saaq"
    plate_other_side["reason"] = "plate_moving_in_other_direction"

    data_removed = pd.concat(
        [
            data_removed,
            null_plate,
            outside_study,
            plate_removed,
            plate_other_side,
            far_from_road,
        ]
    )

    # compute veh direction for veh_data
    veh_data = filter_by_road_network(veh_data, roads)
    veh_data = filter_stays(veh_data)
    veh_data = get_traffic_dir(veh_data, roads)
    veh_data = compute_lpr_lap_sequences(veh_data, method="segment")
    veh_data = compute_veh_direction(veh_data, roads)

    if save_path:
        lpr_data.to_csv(os.path.join(save_path, "lpr_data_enhanced.csv"), index=False)
        veh_data.to_csv(os.path.join(save_path, "veh_data_enhanced.csv"), index=False)
        data_removed.to_csv(
            os.path.join(save_path, "data_removed_by_enhancer.csv"), index=False
        )

    # get origins
    trips = pd.DataFrame()
    if prov_conf.pop("act_prov", False):
        logger.info("computing trips origins.")
        plaques = saaq_data(**prov_conf)
        trips = get_immo_origins(plaques, distance=True)
        if save_path:
            trips.to_csv(os.path.join(save_path, "trips.csv"), index=False)

    return lpr_data, veh_data, trips, data_removed


def filter_by_mask(data, mask):
    """Return and update data filtered.

    Parameters
    ----------
    mask: pandas.Series
        Mask to filter the data.
    """

    data = data.copy()
    data = data[mask]

    return data


def replace_zero_position(
    lpr_data: LprDataFrame, veh_data: TrajDataFrame
) -> LprDataFrame:
    """Infer (0, 0) location on lpr_data with veh_data position.

    Parameters
    ----------
    lpr_data : TrajDataFrame
        Plates position
    veh_data : TrajDataFrame
        Vehicule position

    Returns
    -------
    TrajDataFrame
        Plates position with (0, 0) localisation infered
    """
    lpr_data = lpr_data.copy()
    veh_data = veh_data.copy()

    # index
    veh_data = veh_data.set_index("datetime")
    veh_data = veh_data[~veh_data.index.duplicated(keep="last")]
    time_index = veh_data.index

    veh_data = veh_data.reset_index()

    timestamps = lpr_data.loc[
        (lpr_data["lat"] == 0) | (lpr_data["lng"] == 0), "datetime"
    ].to_list()
    lat_idx = time_index.get_indexer(timestamps, method="nearest")
    lpr_data.loc[(lpr_data["lat"] == 0) | (lpr_data["lng"] == 0), ["lat", "lng"]] = (
        veh_data.loc[lat_idx, ["lat", "lng"]].values
    )

    return lpr_data


def find_vehicule_wayid_for_detection(
    lpr_data: TrajDataFrame, veh_data: TrajDataFrame
) -> TrajDataFrame:
    """Match LPR data to road network using vehicule GPS.

    Parameters
    ----------
    lpt_data : TrajDataFrame
        Plates position.
    veh_data : TrajDataFrame
        Vehicule position.

    Returns
    -------
    TrajDataFrame
        Plates position attached to road network.

    Raises
    ------
    IncompleteDataError
        Columns `segment` must be in veh_data.
    """
    if "segment" not in veh_data.columns:
        raise IncompleteDataError(
            veh_data, "segment", "find_vehicule_wayid_for_detection"
        )

    lpr_data = lpr_data.copy()
    veh_data = veh_data.copy()
    lpr_data = lpr_data.reset_index(drop=True)
    veh_data = veh_data.reset_index(drop=True)
    veh_data = veh_data.set_index([constants.UUID, constants.DATETIME]).sort_index()

    for veh_id in lpr_data[constants.UUID].unique():
        time_index = veh_data.loc[veh_id].index
        lpr_idx = lpr_data[lpr_data[constants.UUID] == veh_id].index

        timestamps = lpr_data.loc[lpr_idx, "datetime"].to_list()
        way_idx = time_index.get_indexer(timestamps, method="ffill")
        not_found_idx = np.argwhere(way_idx == -1).flatten()
        found_idx = np.argwhere(way_idx != -1).flatten()

        lpr_data.loc[lpr_idx[not_found_idx], "segment"] = np.nan
        lpr_data.loc[lpr_idx[found_idx], "segment"] = veh_data.loc[
            itertools.product([veh_id], time_index[way_idx[found_idx]]), "segment"
        ].values

    return lpr_data


def map_side_of_street(arr: pd.Series, mapper: dict) -> pd.Series:
    """Compute side of street by mapper function. This function only
    purpose is the readability in the lapin.enhancement.preprocessing.enhancer
    function.

    Parameters
    ----------
    arr : pd.Series
        Data to map.
    mapper : dict
        Mapper.

    Returns
    -------
    pd.Series
        Data mapped.
    """
    arr = arr.copy()
    return arr.map(mapper)


def compute_side_of_street(side_of_car: pd.Series, veh_dir: pd.Series) -> pd.Series:
    """Side of street is computed by multplying the camera side
    information with the direction of the vehicule.

    Parameters
    ----------
    side_of_car : pd.Series
        1 is right, -1 is left.
    veh_dir : pd.Series
        1 is right, -1 is left.

    Returns
    -------
    pd.Series
        Series of the side of the street.
    """
    return side_of_car * veh_dir
