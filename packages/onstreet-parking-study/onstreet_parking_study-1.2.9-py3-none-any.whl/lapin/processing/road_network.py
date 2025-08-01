""" This module provide enhancing functions relative to a road_network """
import itertools
import datetime
from deprecated import deprecated
import numpy as np
import pandas as pd
import geopandas as gpd

from shapely.geometry import (
    Point,
    LineString
)

from lapin import constants
from lapin.tools.geom import (
    angle_between_vectors,
    azimuth,
    line_azimuth,
    vectorized_r_o_l,
)
from lapin.constants import (
    MONTREAL_CRS,
    DEFAULT_CRS
)
from lapin.tools.utils import IncompleteDataError
from lapin.core import TrajDataFrame
from lapin.core.restrictions import Curbs
from lapin.processing.filter import filter_stays


def project_point_on_line(
    point: Point,
    line: LineString
) -> float:
    """ Wrapper over shapely.Linestring.project to handle NaN value.

    Parameters
    ----------
    point : shapely.Point
        Point to project
    line : shapely.LineString
        LineString to project

    Returns
    -------
    float
        _description_
    """

    if str(line) == 'nan' or str(point) == 'nan':
        return -1

    return line.project(point)


def linear_referencing(
    veh_data: TrajDataFrame,
    roads: gpd.GeoDataFrame,
    roads_id_col: str = constants.SEGMENT,
    mapmatching: bool = True,
    local_crs: str = MONTREAL_CRS
) -> TrajDataFrame:
    """Compute and return the linear reference (LR) of the points onto the
    road.

    Paramaters
    ----------
    veh_data: TrajDataFrame
        Veh GPS
    roads: geopandas.GeoDataFrame
        Geometrie of the roads to match the points onto.
    roads_id_col: str (Default: constants.SEGMENT)
        Column name. Unique identifier for the roads.
    mapmatching: boolean (Default: True)
        Choose matched point instead of collected points.
    local_crs: str (Default: 'epsg:32188')
        CRS of the local aera of the project.

    Return
    ------
    data: TrajDataFrame
        Data with LR computed.
    """

    data = veh_data.copy()

    if 'segment' not in data.columns:
        raise IncompleteDataError(data, 'segment', 'linear_referencing')

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

    # compute linear referencing
    # each point must be projected to compute distance in meters accuratly
    roads = roads.to_crs(local_crs)
    data = data.to_crs(local_crs)

    road_lines = roads.set_index(roads_id_col).loc[data[constants.SEGMENT],
                                                   'geometry']
    points = data.geometry

    # compute projection
    func_dist_on_road = np.vectorize(
        project_point_on_line,
        signature="(),() -> ()"
    )
    data['point_on_segment'] = func_dist_on_road(points, road_lines)

    # convert to traj_dataFrame
    data = data.drop(columns='geometry')
    data = TrajDataFrame(data, parameters=parameters, crs=crs)

    return data


def compare_points_numerization_to_line(
    before_point: Point,
    after_point: Point,
    road_line: LineString
) -> int:
    """ Infer is the direction of a vehicule (set of points) is
    the same as the direction of the numerization of a line

    Parameters
    ----------
    before_point : shapely.Point
        First point recorded for this road_line.
    after_point : shapely.Point
        Last point recorded for this road_line.
    road_line : shapely.LineString
        Linestring of the road

    Returns
    -------
    int
        1 if it's the same direction than the numerisation,
        -1 otherwise.
    """

    azimuth_veh = azimuth(before_point, after_point)
    azimuth_road = line_azimuth(road_line)

    if (
        abs(azimuth_road - azimuth_veh) >= 90 and
        abs(azimuth_road - azimuth_veh) <= 270
    ):
        return -1
    return 1


def compute_dir_veh_for_all_detections(
    lpr_data: TrajDataFrame,
    veh_data: TrajDataFrame,
    roads: gpd.GeoDataFrame,
    mapmatching: bool = False
) -> TrajDataFrame:
    """ Compute the direction of circulation of the vehicule alongside the
    road network. Vehicule direction is computed based on the numerization
    of the LineString of the road.

    Parameters
    ----------
    lpr_data : TrajDataFrame
        Plates position data.
    veh_data : TrajDataFrame
        Vehicules position data.
    roads : gpd.GeoDataFrame
        Geography of the roads.
    mapmatching : bool, optional
        Use mapmatched position or raw position, by default False.

    Returns
    -------
    TrajDataFrame
        Plates position with vehicule direction computed.
    """

    lpr_data = lpr_data.copy()
    veh_data = filter_stays(veh_data)
    lpr_data = lpr_data.reset_index(drop=True)
    veh_data = veh_data.reset_index(drop=True)

    veh_data = veh_data.set_index([constants.UUID,
                                   constants.DATETIME]).sort_index()

    lat_col = 'lat'
    lng_col = 'lng'
    if mapmatching:
        lat_col += '_match'
        lng_col += '_match'

    for veh_id in lpr_data[constants.UUID].unique():
        time_index = veh_data.loc[veh_id].index
        lpr_idx = lpr_data[lpr_data[constants.UUID] == veh_id].index

        before_time = (
            lpr_data.loc[lpr_idx, constants.DATETIME].copy() -
            datetime.timedelta(seconds=-1)
        )
        after_time = (
            lpr_data.loc[lpr_idx, constants.DATETIME].copy() +
            datetime.timedelta(seconds=1)
        )

        before_idx = time_index.get_indexer(before_time, method='ffill')
        after_idx = time_index.get_indexer(after_time, method='bfill')

        found_idx = np.intersect1d(
            np.argwhere(before_idx != -1).flatten(),
            np.argwhere(after_idx != -1).flatten()
        )
        lpr_idx_f = lpr_idx[found_idx]

        before_points = veh_data.loc[
            itertools.product(
                [veh_id],
                time_index[before_idx[found_idx]]
            ), [lng_col, lat_col]
        ].values
        after_points = veh_data.loc[
            itertools.product(
                [veh_id],
                time_index[after_idx[found_idx]]
            ), [lng_col, lat_col]
        ].values

        roads_lines = roads.set_index(constants.SEGMENT).loc[
            lpr_data.loc[lpr_idx_f, constants.SEGMENT],
            'geometry'
        ].values

        func_dir_veh = np.vectorize(
            compare_points_numerization_to_line,
            signature='(2),(2),() -> ()'
        )
        lpr_data.loc[lpr_idx_f, 'dir_veh'] = func_dir_veh(
            before_points,
            after_points,
            roads_lines
        )

    return lpr_data


def compute_veh_direction(
    veh_data: TrajDataFrame,
    roads: gpd.GeoDataFrame
) -> TrajDataFrame:
    """ Compute the vehicules direction along the geometry of the roads.
    Direction is determined with the digitalization order of the geometry
    of the road.

    Parameters
    ----------
    veh_data : TrajDataFrame
        Vehicule position data.
    roads : gpd.GeoDataFrame
        Geometry of the roads.

    Returns
    -------
    TrajDataFrame
        Vehicule position data with infered vehicule direction.
    """
    veh_data = filter_stays(veh_data)

    # compute the sequence of each vehicule on each road
    veh_data['seq'] = veh_data.groupby(constants.UUID)[constants.SEGMENT]\
                              .transform(lambda x: (x.diff() != 0).cumsum())

    # vectorized information for get_dir_veh_on_road
    before_points = veh_data.groupby(
        [constants.UUID, 'seq']
    )[['lng', 'lat']].transform('first').values
    after_points = veh_data.groupby(
        [constants.UUID, 'seq']
    )[['lng', 'lat']].transform('last').values

    segs = veh_data.groupby(
        [constants.UUID, 'seq']
    )['segment'].transform('first').values

    roads_lines = roads.set_index(constants.SEGMENT).loc[segs,
                                                         'geometry'].values

    func_dir_veh = np.vectorize(
        compare_points_numerization_to_line,
        signature='(2),(2),() -> ()'
    )
    veh_data['dir_veh'] = func_dir_veh(
        before_points,
        after_points,
        roads_lines
    )

    veh_data = veh_data.drop(columns='seq')

    return veh_data


def get_traffic_dir(
    veh_data: TrajDataFrame,
    roads: gpd.GeoDataFrame
) -> TrajDataFrame:
    """ Associate the traffic direction of the roads to
    the vehicule position.

    Parameters
    ----------
    veh_data : TrajDataFrame
        Vehicule position data.
    roads : gpd.GeoDataFrame
        Geometry of the roads.

    Returns
    -------
    TrajDataFrame
        Vehicule position data.

    Raises
    ------
    IncompleteDataError
        roads must have ID_TRC and SENS_CIR columns.
    IncompleteDataError
        veh_data must have segment column.
    """

    if constants.SEGMENT not in roads.columns:
        raise IncompleteDataError(
            roads,
            constants.SEGMENT,
            'Roads data should have a ID_TRC column to specify unique ID.'
        )
    if constants.TRAFFIC_DIR not in roads.columns:
        raise IncompleteDataError(
            roads,
            constants.TRAFFIC_DIR,
            'Roads data should have SENS_CIR column to specify traffic dir.'
        )
    if 'segment' not in veh_data.columns:
        raise IncompleteDataError(
            veh_data,
            'segment',
            'Vehicule data should have segment column to specify road ID.'
        )

    veh_data = veh_data.copy()
    veh_data = veh_data.join(
        other=roads.set_index(constants.SEGMENT)[constants.TRAFFIC_DIR],
        on='segment',
        how='left'
    )
    veh_data = veh_data.rename(columns={constants.TRAFFIC_DIR: 'traffic_dir'})

    return veh_data


@deprecated(
    reason='With the change of system, we now use ' +
    'lapin.enhancer.preprocessing.compute_side_of_street function.'
)
def compute_geometric_side_of_street(
    data,
    roads,
    roads_id_col,
    data_road_col='segment',
    lat_c=constants.LATITUDE,
    lng_c=constants.LONGITUDE
):
    """Compute and return the side of street of the point collected as
    the position of the point in regard to the matched road segment.

    Parameters
    ----------
    roads: geopandas.GeoDataFrame
        Geometrie of the roads to match the points onto.
    roads_id_col: str (Default: constants.SEGMENT)
        Column name. Unique identifier for the roads.
    data_road_col: str (Default: 'segment')
        Column name. Unique identifier for the roads in data.
    lat_c: str (Default: 'lat')
        Column name for the latitude coordinate in data.
    lng_c: str (Default: 'lng')
        Column name for the latitude coordinate in data.

    Return
    ------
    data: pandas.DataFrame
        Data with side_of_street computed.

    Raises
    ------
    IncompleteDataError
        data must have dir_veh computed first.
    """
    data = data.copy()
    if 'dir_veh' not in data.columns:
        raise ValueError("Column dir_veh must be created first.")

    # list of roads line
    roads_lines = pd.merge(
        data,
        roads,
        how='left',
        left_on=data_road_col,
        right_on=roads_id_col
    )['geometry']

    # list of points
    points = np.array(list(map(Point, data[lng_c], data[lat_c])), dtype=object)

    # vectorized func
    data['side_of_street'] = vectorized_r_o_l(roads_lines, points)

    return data


def add_segment_geom(
    data: TrajDataFrame,
    roads_geoms: gpd.GeoDataFrame
) -> TrajDataFrame:
    """ Add column segment_geodbl_geom. This columns correspond to
    the geometry of the geobase double passed in input.

    Parameters
    ----------
    data: TrajDataFrame
        Position data.
    geobaseDouble : pd.DataFrame.
        Geometry og road netwoork with side of street. Segment ID must
        be the same as used in Enhancer data.

    Returns
    -------
    data : pd.DataFrame
        Data with geometry column segment_geodbl_geom added.
    """
    data = data.copy()

    data = data.join(
        other=roads_geoms.set_index(
            [constants.SEGMENT,
             constants.SIDE_OF_STREET]
        )[constants.SEG_DB_GIS],
        on=['segment', 'side_of_street']
    )

    return data


def get_car_direction_along_street(
    data: pd.DataFrame,
    roads: gpd.GeoDataFrame,
    roads_id_col: str = constants.SEGMENT,
    use_roadmatching: bool = True
) -> pd.DataFrame:
    '''Compute the direction of the LPD car on the segment for each lap

    Parameters
    ---------
    data: pandas.DataFrame
        Position of vehicule.
    roads: geopandas.GeoDataFrame
        Road netword GeoDataFrame
    use_roadmatching: bool, optional
        Indicate to use road matched latitude and longitude or not. If
        not, the raw data is used, by default True.

    Return
    ------
    data: pd.DataFrame.
        Ehancer data, with direction of LPD car computed. Columns dir_veh is
        added.

    Raises
    ------
    ValueError
        Data must have column lap.
    ValueError
        Data must have columns lat_match, lng_match if use_roadmatching = True.
    '''
    data = data.copy()
    if 'lap' not in data.columns:
        raise ValueError("Column lap must be created first.")
    if use_roadmatching and 'lat_match' not in data.columns:
        raise ValueError(
            "When using roadmatching, column lat_matched" +
            "and lng_matched must be created first."
        )

    if use_roadmatching:
        lat_c, lng_c = ('lat_match', 'lng_match')
    else:
        lat_c, lng_c = ('lat', 'lng')

    groups = []
    for (segment, _), group in data.groupby(['segment', 'lap']):
        if group.shape[0] == 1:
            group['dir_veh'] = -2
            groups.append(group)
            continue

        group.sort_values(['datetime'], inplace=True)

        # get road direction
        (road_x,
         road_y) = roads[roads[roads_id_col] == segment].geometry.iloc[0].xy
        road_x = np.array(road_x)[[0, -1]]
        road_y = np.array(road_y)[[0, -1]]
        road_vec = LineString([[road_x[0], road_y[0]], [road_x[1], road_y[1]]])

        # get vehicule direction
        lap_x = group.iloc[[0, -1]][lng_c].values
        lap_y = group.iloc[[0, -1]][lat_c].values

        if (
            lap_x.size <= 1 or
            (lap_x[0] == lap_x[1] and
             lap_y[0] == lap_y[1])
        ):
            group['dir_veh'] = -2
            groups.append(group)
            continue

        lap_vec = LineString([[lap_x[0], lap_y[0]], [lap_x[1], lap_y[1]]])

        group['dir_veh'] = 1 if angle_between_vectors(
            road_vec,
            lap_vec,
            as_degree=True
        ) <= 90 else -1
        groups.append(group)

    data = pd.concat(groups)

    return data


@deprecated(
    reason='Replaced by lapin.core.study.CollectedArea'
)
def enforce_both_side_of_street(
    data: pd.DataFrame,
    segment_to_enforce: list,
    restriction_handler: Curbs
):
    """ This function add blank data for missing edge of the road network by
    making sure that the entierty of the road network is present in the
    data. An edge in the road network is defined as the side of one street
    between two other street.

    Parameters
    ----------
    data: pandas.DataFrame
        Data on each edge of the road network
    segment_to_enforce: List[int]
        List of edge's id to assert presence on
    restriction_handler: restrictions.RestrictionHandler
        Restriction handling class

    Returns
    -------
    pandas.DataFrame
        Data with each edges present
    """

    data = data.copy()
    data.datetime = pd.to_datetime(data.datetime)

    data_to_enforce = data[
        data[constants.SEGMENT].isin(segment_to_enforce)
    ].copy()

    # check if there is at least one vehicule scan on each side of street
    side_of_street_count = data_to_enforce[['segment',
                                            'side_of_street',
                                            'lap_id']].drop_duplicates()
    missing_data = side_of_street_count[
        side_of_street_count.groupby(['segment',
                                      'lap_id']).transform('size') < 2
    ].copy()

    # create fake data where it's missing
    missing_data.side_of_street = missing_data.side_of_street.map({
        1: -1,
        -1: 1
    })
    missing_data['datetime'] = data_to_enforce.loc[missing_data.index,
                                                   'datetime']
    # recover capacity for this segment
    missing_data_cap = missing_data.apply(
        lambda x: restriction_handler.get_segment_capacity(x.segment,
                                                           x.side_of_street,
                                                           x.datetime),
        axis=1)

    # fill columns with missing data
    capacity_cols = ['nb_places_total']
    missing_data.loc[missing_data_cap.index,
                     capacity_cols] = missing_data_cap

    cols_enforced = list(set(data_to_enforce.columns) -
                         set(missing_data.columns))
    missing_data[cols_enforced] = data_to_enforce.loc[missing_data.index,
                                                      cols_enforced]

    # set restriction to 1 to discard
    missing_data['is_restrict'] = np.nan
    missing_data['restrictions'] = np.nan

    return pd.concat([data, missing_data], axis=0, ignore_index=True)


@deprecated(
    reason='Replaced by lapin.core.study.CollectedArea'
)
def aggregate_one_way_street(
    lapin_df: pd.DataFrame,
    road_gdf: gpd.GeoDataFrame,
    seg_geom: gpd.GeoDataFrame,
    restriction_handler: Curbs,
    ignore_seg_ids: list = None
) -> tuple:
    """ Aggregate lectures on both side of the street for one way street

    Parameters
    ----------
    lapin_df: pd.DataFrame
        LAPI hit dataframe
    raod_gdf: gpd.GeoDataFrame
        Filament representation of road network
    seg_geom: gpd.GeoDataFrame
        Curb representation of road network
    ignore_seg_ids: list, default: None
        List of segment's id to ignore during aggregation

    Returns
    -------
    tuple
        Both updated count in lapin_df and updated geometry in seg_geom
    """

    # Assert that columns are present in data
    # lapin_df
    cols_lapin_assert = [
        constants.CAP_N_VEH,
        'lap_id',
    ]
    assert all(col in lapin_df.columns for col in cols_lapin_assert)

    # segments
    cols_segments_assert = [
        constants.SEGMENT,
        constants.TRAFFIC_DIR,
    ]
    assert all(col in road_gdf.columns for col in cols_segments_assert)

    # seg_geom
    cols_seg_geom_assert = [
        'COTE',
        constants.SEG_DB_GIS,
    ] + cols_segments_assert
    assert all(col in seg_geom.columns for col in cols_seg_geom_assert)

    ignore_seg_ids = list(ignore_seg_ids or [])

    # Update side_of_street
    seg_geom[constants.SIDE_OF_STREET_VIZ] = seg_geom['COTE'].copy()
    seg_geom.loc[
        seg_geom[constants.TRAFFIC_DIR].isin([-1, 1])
        & ~seg_geom[constants.SEGMENT].isin(ignore_seg_ids),
        constants.SIDE_OF_STREET_VIZ
    ] = 'Aucun'
    seg_geom[constants.SIDE_OF_STREET_VIZ] = seg_geom[
        constants.SIDE_OF_STREET_VIZ
    ].map(constants.SEG_DB_SIDE_OF_STREET_MAP)

    # assert that every side_of_street is represented
    segment_to_agg = list(
        set(road_gdf.loc[road_gdf[constants.TRAFFIC_DIR].isin([-1, 1]),
                         constants.SEGMENT]) -
        set(ignore_seg_ids)
    )
    lapin_df = enforce_both_side_of_street(
        lapin_df,
        segment_to_agg,
        restriction_handler
    )

    # compute side_of_street
    lapin_df[constants.SIDE_OF_STREET_VIZ] = \
        lapin_df[constants.SIDE_OF_STREET].copy()
    lapin_df.loc[
        lapin_df.segment.isin(segment_to_agg),
        constants.SIDE_OF_STREET_VIZ
    ] = 0

    # update geometry
    seg_geom = seg_geom.join(
        other=road_gdf.set_index([constants.SEGMENT])['geometry'],
        on=[constants.SEGMENT]
    )
    mask = (
        seg_geom[constants.TRAFFIC_DIR].isin([-1, 1]) &
        ~seg_geom[constants.SEGMENT].isin(ignore_seg_ids)
    )
    seg_geom.loc[mask, constants.SEG_DB_GIS] = seg_geom.loc[mask, 'geometry']
    seg_geom.drop(columns='geometry', inplace=True)
    seg_geom['COTE_RUE_ID'] = (
        seg_geom[constants.SEGMENT].astype(int).astype(str) +
        seg_geom[constants.SIDE_OF_STREET_VIZ].replace({-1: 2}).astype(str)
    ).astype(int)

    # remove duplicates
    seg_geom = seg_geom.loc[seg_geom['COTE_RUE_ID'].drop_duplicates().index]

    # update nb_place
    lapin_df[constants.CAP_N_VEH] = lapin_df.apply(
        lambda x: np.array([x[constants.SIDE_OF_STREET],
                            x[constants.CAP_N_VEH]]),
        axis=1
    )
    lapin_df[constants.CAP_N_VEH] = (
        lapin_df
        .groupby([constants.SEGMENT,
                  constants.SIDE_OF_STREET_VIZ,
                  'lap_id'])[[constants.CAP_N_VEH]]
        .transform(
            lambda x:
                np.sum(
                    np.unique(
                        np.array(list(x)),
                        axis=0
                    )[:, 1]
                )
        )
    )

    # remove added lecture by function <__main__.enforce_both_side_of_street>
    lapin_df = lapin_df[~lapin_df.is_restrict.isna()].copy()
    lapin_df[constants.CAP_IS_RESTRICT] = \
        lapin_df[constants.CAP_IS_RESTRICT].astype(bool)

    return lapin_df, seg_geom
