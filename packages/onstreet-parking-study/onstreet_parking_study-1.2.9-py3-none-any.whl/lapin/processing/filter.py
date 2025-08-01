""" Filtering function """

import re
import logging

import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from shapely import Point

from lapin import constants
from lapin.core import TrajDataFrame, LprDataFrame
from lapin.processing.utils import pairwise, get_mask_avenue
from lapin.processing.lap import _lap_sequence_by_seg
from lapin.tools.utils import IncompleteDataError
from lapin.tools.geom import vectorized_dist, localisation_distance

logger = logging.getLogger(__name__)


def filter_by_road_network(
    veh_data: TrajDataFrame, roads: gpd.GeoDataFrame
) -> TrajDataFrame:
    """Filter veh_position on specific road network

    Parameters
    ----------
    veh_data : TrajDataFrame
        Vehicule data to filter.
    roads : gpd.GeoDataFrame
        Road network.

    Returns
    -------
    TrajDataFrame

    Raises
    ------
    IncompleteDataError
        segment must be in veh_data
    """
    veh_data = veh_data.copy()
    if constants.SEGMENT not in veh_data.columns:
        raise IncompleteDataError(veh_data, constants.SEGMENT, "filter_by_road_network")

    seg_id = roads[constants.SEGMENT].unique()

    return veh_data[veh_data[constants.SEGMENT].isin(seg_id)]


def compute_speed(veh_data: TrajDataFrame) -> list[float]:
    """Compute speed between each points

    Parameters
    ----------
    veh_data : TrajDataFrame
        Vehicule position

    Returns
    -------
    list[float]
        speed in m.s-1
    """
    veh_data = veh_data.copy()

    if veh_data.shape[0] <= 1:
        return []

    dist_f = np.vectorize(localisation_distance, signature="(2), (2) -> ()")

    points = veh_data[[constants.LATITUDE, constants.LONGITUDE]].values
    distance = dist_f(points[:-1], points[1:])

    timedelta = veh_data[constants.DATETIME].diff().values[1:] / np.timedelta64(1, "s")

    return distance / timedelta


def filter_stays(veh_data: TrajDataFrame) -> TrajDataFrame:
    """Remove row where the vehicule is not moving.

    Parameters
    ----------
    veh_data : TrajDataFrame
        Vehicule position.

    Returns
    -------
    TrajDataFrame
        Vehicule position with stays removed.
    """

    veh_data = veh_data.copy()
    veh_data = _lap_sequence_by_seg(veh_data)

    new_veh_data = []
    add_veh_data = new_veh_data.append

    for _, data in veh_data.groupby([constants.UUID, "primary_lap"]):
        data["speed"] = np.pad(
            compute_speed(data), (1, 0), "constant", constant_values=(np.nan,)
        )

        keep = data["speed"] > 0.5
        keep.iloc[0] = True
        keep.iloc[-1] = True

        add_veh_data(data[keep])

    return pd.concat(new_veh_data)


def filter_side_of_street_on_2_way_street(
    data: TrajDataFrame,
    roads: pd.DataFrame,
    roads_id_col: str = constants.SEGMENT,
    traffic_dir_col: str = constants.TRAFFIC_DIR,
) -> pd.DataFrame:
    """Re-assign the side of street of parking event seen on the wrong side
    when street is a 2 way street.

    Parameters
    ----------
    data: TrajDataFrame
        Plates position data.
    road_database: pd.DataFrame
        Road network representation.
    roads_id_col: str, optional
        Name of the columns containing id's of road segments, by default
        'ID_TRC'.
    traffic_dir_col: str, optional
        Name of the columns containing road segments traffic direction, by
        default 'SENS_CIR'.

    Returns
    -------
    pd.DataFrame:
        Plate data filtered.

    Raises
    ------
    IncompleteDataError:
        data must have a column dir_veh.
    IncompleteDataError:
        data must have a column side_of_street.

    """

    data = data.copy()
    roads = roads.copy()

    # check that columns are created
    if "dir_veh" not in data.columns:
        raise IncompleteDataError(
            data, "dir_veh", "clean_side_of_street_on_2_way_street"
        )
    if "side_of_street" not in data.columns:
        raise IncompleteDataError(
            data, "side_of_street", "clean_side_of_street_on_2_way_street"
        )

    # save data_columns
    original_columns = data.columns

    data.drop(columns=traffic_dir_col, inplace=True, errors="ignore")
    data = data.join(
        other=roads[[roads_id_col, traffic_dir_col]].set_index(roads_id_col),
        on=["segment"],
        how="left",
    )

    # side of street enforcement
    data_rm = data[
        (
            (data[traffic_dir_col] == 0)
            & (data.dir_veh != -2)
            & (data.dir_veh != data.side_of_street)
        )
    ]
    logger.info(
        "%s plates where encoutered on the left on 2 way street.", data_rm.shape[0]
    )

    data = data[
        ~(
            (data[traffic_dir_col] == 0)
            & (data.dir_veh != -2)
            & (data.dir_veh != data.side_of_street)
        )
    ]

    data.loc[(data[traffic_dir_col] == 0) & (data.dir_veh != -2), "side_of_street"] = (
        data.loc[(data[traffic_dir_col] == 0) & (data.dir_veh != -2)].dir_veh
    )

    data = data[original_columns]

    return data, data_rm


def filter_plates(
    data: LprDataFrame, personalized_plates: bool = False
) -> tuple[LprDataFrame, LprDataFrame]:
    """Drop readings that are noise readings.

    Personalized plates based on :
    https://saaq.gouv.qc.ca/immatriculation/plaque-immatriculation-personnalisee

    Normal plates based on :
    https://saaq.gouv.qc.ca/immatriculation/categories-plaques-immatriculation

    # keep this here in case it will come to use
    to_remove = r'[B8][AR]*R\w*|TR[O0]*[TT]*[0O]*[I1]R\w*|[E]*C[0O][L]*[1I]*E[R]*|[U]*TL[1I]SER|P[O0]{0,1}LICE'

    Parameters
    ----------
    personalized_plates: boolean (Default: False)
        Indicator to keep personalized plates in the data.

    Returns
    -------
    LprDataFrame
        Data filtered.
    LprDataFrame
        Data removed.
    """
    data = data.copy()

    # personalized plates from 5 to 7 chars
    personized_plates_57 = r"[a-z]{0,2}[a-z]{5}|\d[a-z]{4,6}|[a-z]{4,6}"
    personized_plates_24 = r"\w{2,4}"

    # normal plates
    promenade = (
        r"\d{3}[a-z]{3}|\d{3}H\d{3}|[a-z]{3}\d{3}|"
        + r"[a-z]\d{2}[a-z]{3}|[a-z]{3}\d{2}[a-z]|\d{2}[a-z]{4}"
    )
    promenade_cc_cd = r"c[cd]\d{4}"
    commercial = r"f[a-z]{2}\d{4}"
    trailer = r"r[a-z]\d{4}[a-z]"
    five_digit = r"(a|ae|ap|au)\d{5}"
    six_digit = r"(c|l|f)\d{6}"
    radio = r"(VA2|VE2)[a-z]{2,3}"
    electric = r"[vcl]\d{3}1VE$|c[cd]\d1VE"
    movable = r"x[0-9a-z]\d{5}"
    other = r"[cf][a-z]{3}\d{3}"

    if personalized_plates:
        patterns = [
            personized_plates_57,
            personized_plates_24,
            promenade,
            promenade_cc_cd,
            commercial,
            trailer,
            five_digit,
            six_digit,
            radio,
            electric,
            movable,
            other,
        ]
    else:
        patterns = [
            promenade,
            promenade_cc_cd,
            commercial,
            trailer,
            five_digit,
            six_digit,
            radio,
            electric,
            movable,
            other,
        ]

    compiled_plates = re.compile(
        r"^(" + "|".join(x for x in patterns) + r")", re.IGNORECASE
    )

    # filter plates
    data_f = data[
        data[constants.PLATE].apply(
            lambda x: True if re.match(compiled_plates, x) else False
        )
    ]
    data_index = data.index

    # print removed plates
    removed_plaque = " ; ".join(
        data[~data_index.isin(data_f.index)][constants.PLATE].sort_values().unique()
    )

    # removed plates
    data_rm = data[~data_index.isin(data_f.index)]

    logger.debug(
        "%s perc. of records were removed. Containing %s uniques plates.",
        data_rm.shape[0] / data.shape[0] * 100,
        len(removed_plaque),
    )
    logger.debug("Plates removed by the process %s", removed_plaque)

    return data_f, data_rm


def denoize_plates(data: LprDataFrame) -> LprDataFrame:
    """Function to remove noize from the OCR perform on plates.

    Done by clustering plates along Damerau-Levenshtein Distance.

    Parameters
    ----------
    data: LprDataFrame
        Plates data.

    Returns
    -------
    data: pd.DataFrame.
        Data with plates reading cleansed.

    Raise
    -----
    ValueError
        Data must have segment and side_of_street columns.
    """
    data = data.copy()

    if "segment" not in data.columns:
        raise ValueError("Column segment must be created first.")
    if "side_of_street" not in data.columns:
        raise ValueError("Column segment must be created first.")

    res = []
    test = False
    plates_changed = {}
    for (seg, side), df in data.groupby(["segment", "side_of_street"]):
        plates = df[constants.PLATE].drop_duplicates().values
        pdist = pairwise(list(plates))
        dbsc = DBSCAN(eps=1, min_samples=1, metric="precomputed").fit(pdist)

        labels, counts = np.unique(dbsc.labels_, return_counts=True)
        for label in labels[counts > 1]:
            test = True
            p_list = plates[dbsc.labels_ == label]
            c_center = (
                df[df[constants.PLATE].isin(p_list)][constants.PLATE]
                .value_counts()
                .index[0]
            )
            p_dict = {}
            for p in p_list:
                p_dict[p] = c_center
            df.replace({constants.PLATE: p_dict}, inplace=True)
            plates_changed[(seg, side, c_center)] = list(p_list)
        res.append(df)

    if test:
        logger.debug("Les plaques suivante ont changés de nom : %s", plates_changed)
    data = pd.concat(res)

    return data


def clean_data(data, roads, roads_id_col, distance=8, street_name=None):
    """Perform cleaning operation sequentially.
        1. Remove_points_far_from_road
        2. Filter plates
        3. Drop duplicates scan
        4. Remove street if wanted

    Parameters
    ----------
    roads: gpd.GeoDataFrame
        Geometry of roads.
    roads_id_col: string
        Name of ID columns of roads.
    distance: int (Default: 8)
        Remove points at this distance of a road. In meter.
    street_name: string (Default: '')
        Name of the street to remove from the data.
    Returns
    -------
    data: pd.DataFrame.
        Data cleaned.
    """
    # remove too far points
    data.remove_points_far_from_road(roads, roads_id_col, distance)
    # denoize plates
    data.denoize_plates()
    # filter plates data
    data.filter_plates()
    # drop duplicates
    try:
        data.drop_duplicate_scan()
    except ValueError as val_err:
        logger.error("duplicates recording could not be removed : %s", str(val_err))
    # remove street
    if street_name:
        mask = get_mask_avenue(data, roads, avenue=street_name)
        data.filter_by_mask(mask)

    # get data
    data = data.copy()

    return data


def remove_noizy_readings(
    data: TrajDataFrame,
    roads: gpd.GeoDataFrame,
    roads_id_col: str = constants.SEGMENT,
    threshold: int = 2,
) -> TrajDataFrame:
    """_summary_

    Parameters
    ----------
    data : pd.DataFrame
        _description_
    road_database : gpd.GeoDataFrame
        _description_
    idx_road_col : str, optional
        _description_, by default 'ID_TRC'
    threshold : int, optional
        _description_, by default 2

    Returns
    -------
    pd.DataFrame
        _description_

    Raises
    ------
    IncompleteDataError
        _description_
    IncompleteDataError
        _description_
    IncompleteDataError
        _description_
    """

    data = data.copy()
    roads = roads.copy()

    # check that columns are created
    if "side_of_street" not in data.columns:
        raise IncompleteDataError(data, "side_of_street", "remove_noizy_readings")
    if "lap_id" not in data.columns:
        raise IncompleteDataError(data, "lap_id", "remove_noizy_readings")
    if "nb_places_total" not in data.columns:
        raise IncompleteDataError(data, "nb_places_total", "remove_noizy_readings")
    if constants.SEGMENT not in roads.columns:
        raise IncompleteDataError(roads, constants.SEGMENT, "remove_noizy_readings")

    # save data_columns
    original_columns = data.columns

    # computing number of veh on segment per lap
    data["nb_occurence"] = data.groupby(
        ["segment", "side_of_street", "lap_id"]
    ).transform("size")

    roads["length"] = roads.to_crs("epsg:32188").length

    data.drop(columns="length", inplace=True, errors="ignore")
    data = data.join(
        other=roads[[roads_id_col, "length"]].set_index(roads_id_col),
        on=["segment"],
        how="left",
    )

    # Compute minimal distance between each point and the start of the segment
    # We've seen that sometimes there is points that get associated with
    # perpendicular street. Thoose point have a hudge impact on the mean
    # occupancy of the street.
    data = data.assign(
        delta_beg_end_seg=np.minimum(
            (data.length - data.point_on_segment).abs(),
            (0 - data.point_on_segment).abs(),
        )
    )
    data = data.assign(quart_length=data.length / 4)

    # Filter all points on a segment if :
    #   - there count is bellow threshold,
    #   - the capacity of the street is above 5*threshold
    #   - there position is close to the begining or the end of a segment
    data = data[
        ~(
            (data.nb_occurence <= threshold)
            & (data.nb_places_total > 5 * threshold)
            & (data.delta_beg_end_seg < data.quart_length)
        )
    ]

    return data[original_columns]


def drop_duplicate_scan(data: pd.DataFrame) -> pd.DataFrame:
    """Clean double readings in data. Doublons are determined by
    columns ['lap_id', 'segment', 'side_of_street', 'plaque'].

    Returns
    -------
    data: pd.DataFrame
        Enhancer data cleaned from doublons.

    Raise
    -----
    ValueError:
        data must have lap_id column.
    ValueError:
        data must have segment column.
    ValueError:
        data must have side_of_street column.
    ValueError:
        data must have plaque column.
    """

    data = data.copy()

    if "lap_id" not in data.columns:
        raise ValueError("Column lap_id must be created first.")
    if "segment" not in data.columns:
        raise ValueError("Column semgent must be created first.")
    if "side_of_street" not in data.columns:
        raise ValueError("Column side_of_street must be created first.")
    if "plate" not in data.columns:
        raise ValueError("Column plaque must be in the DataFrame.")

    data = data[
        data.index.isin(
            data[["lap_id", "segment", "side_of_street", "plate"]]
            .drop_duplicates(keep="first")
            .index
        )
    ]

    return data


def remove_points_far_from_road(
    data: TrajDataFrame, roads: gpd.GeoDataFrame, roads_id_col: str, distance: int = 8
):
    """Clean data points that are far aside from the road segment.

    Paramaters
    ----------
    data: TrajDataFrame
        Position data.
    roads: gpd.GeoDataFrame.
        GeoDataFrame of the road networks.
    roads_id_col: string.
        Column name of road identifier.
    distance: int, optional
        Determine the buffer to classify noise points in meters, by default 10.

    Raises
    ------
    ValueError

    """

    data = data.copy()
    if "segment" not in data.columns:
        raise ValueError("Column segment must be created first.")
    if not isinstance(roads, gpd.GeoDataFrame):
        raise ValueError("Roads must be a GeoDataFrame")

    # roads to data crs
    roads.to_crs(data.crs, inplace=True)

    # list of roads line
    roads_lines = pd.merge(
        data,
        roads.rename_geometry("roads_lines"),
        how="left",
        left_on="segment",
        right_on=roads_id_col,
    )["roads_lines"]

    # list of points
    points = np.array(
        list(map(Point, data[constants.LONGITUDE], data[constants.LATITUDE])),
        dtype=object,
    )

    # compute distance
    dists = vectorized_dist(roads_lines, points)

    # remove far points
    data_rm = data[dists >= distance].copy()
    data = data[dists < distance].copy()

    return data, data_rm


def remove_veh_parked_on_restrictions(lpr_data: LprDataFrame) -> LprDataFrame:
    """Remove plate read that were on a no parking zone.

    Parameters
    ----------
    lpr_data : LprDataFrame
        Plate dataframe. Must have the regulation associated with them.

    Returns
    -------
    LprDataFrame
        Filtered plate dataframe.

    Raises
    ------
    IncompleteDataError
        Application of the restriction must be done before filtering
        the plates.
    """
    if constants.CAP_IS_RESTRICT not in lpr_data.columns:
        raise IncompleteDataError(
            lpr_data,
            constants.CAP_IS_RESTRICT,
            "Please apply restriction before filtering",
        )

    return lpr_data[~lpr_data[constants.CAP_IS_RESTRICT]].copy()
