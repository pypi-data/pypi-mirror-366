""" This module rovide a helper class for the matching among diferent
interfaces
"""

import json
import logging
import requests
import pandas as pd
import numpy as np
import geopandas as gpd
import osrm

from lapin import constants
from lapin.core import TrajDataFrame
from lapin.tools.geom import distance_line_from_point

logger = logging.getLogger(__name__)

# Matcher
OSRM_MATCH_COLUMNS = ["lat_match", "lng_match"]
OSRM_2_MATCHER = {
    "u": "u",
    "v": "v",
    "lat_match": "lat_match",
    "lng_match": "lng_match",
}

VALHALLA_MATCH_COLUMNS = [
    "lng_match",
    "lat_match",
    "type",
    "edge_index",
    "end_route_discontinuity",
    "point_on_segment",
    "segment",
    "nxt_segment",
    "prv_segment",
]

VALHALLA_FILTERS = {
    "attributes": [
        "edge.way_id",
        "matched.point",
        "matched.type",
        "matched.edge_index",
        "matched.begin_route_discontinuity",
        "matched.end_route_discontinuity",
        "matched.distance_along_edge",
    ],
    "action": "include",
}


class NpEncoder(json.JSONEncoder):
    """Numpy data JSON encoder."""

    def default(self, obj):
        """Default encoding function.

        Parameters
        ----------
        obj : dict | list
            Json object

        Returns
        -------
        str
            Encoded json object
        """
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def build_request_valhalla(
    tdf: TrajDataFrame, costing="auto", shape_match="map_snap", **kwargs
):
    """_summary_

    Parameters
    ----------
    tdf : TrajDataFrame
        _description_
    costing : str, optional
        _description_, by default 'auto'
    shape_match : str, optional
        _description_, by default 'map_snap'

    Returns
    -------
    _type_
        _description_
    """
    payload = {}
    tdf["time"] = list(tdf.datetime.values.astype(np.int64) // 10**9)
    payload["shape"] = (
        tdf[["lat", "lng", "time"]]
        .rename(columns={"lng": "lon"})
        .to_dict(orient="records")
    )
    payload["costing"] = costing
    payload["shape_match"] = shape_match

    payload.update(kwargs)

    return payload


def create_valhalla_payload(
    coords: list[tuple[float, float]],
    costing: str = "auto",
    shape_match: str = "match_snap",
    **kwargs,
) -> dict:
    """Create the paylod for valhalla

    Parameters
    ----------
    coords : List[Tuple[float, float]]
        Latitude, Longitude pairs.
    costing : str, optional
        Costing parameter, by default 'auto'.
    shape_match : str, optional
        Algorithm for the matching, by default 'match_snap'.
    **kwargs
        Accept ''
    """

    payload = {}

    columns = ["lat", "lon"]
    df = pd.DataFrame(coords, columns=columns)

    if "timestamps" in kwargs:
        df["time"] = kwargs.pop("timestamps")
        df["time"] = df["time"].astype(int)
        columns += ["time"]

    payload["shape"] = df[columns].to_dict(orient="records")
    payload["costing"] = costing
    payload["shape_match"] = shape_match

    payload.update(kwargs)

    return payload


def get_closest_roads_id(point, road1, road2, id1, id2):
    """_summary_

    Parameters
    ----------
    point : _type_
        _description_
    road1 : _type_
        _description_
    road2 : _type_
        _description_
    id1 : _type_
        _description_
    id2 : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    # if distance is too big return 0
    if (
        distance_line_from_point(road1, point) > 10
        and distance_line_from_point(road2, point) > 10
    ):
        return np.nan
    if distance_line_from_point(road1, point) < distance_line_from_point(road2, point):
        return id1
    else:
        return id2


def infer_interpolated_way_id(roads, match_points):
    """_summary_

    Parameters
    ----------
    roads : _type_
        _description_
    match_points : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    match_points = match_points.copy()
    roads = roads.copy()
    roads = roads.set_index(constants.SEGMENT)

    match_points["nxt_segment"] = match_points["segment"].ffill()
    match_points["prv_segment"] = match_points["segment"].bfill()

    match_points["prv_segment"] = match_points["prv_segment"].fillna(-1).astype(int)
    match_points["nxt_segment"] = match_points["nxt_segment"].fillna(-1).astype(int)

    mask = (
        match_points["type"].isin(["interpolated", "unmatched"])
        & match_points.segment.isna()
        & (match_points.prv_segment != -1)
        & (match_points.nxt_segment != -1)
        & match_points.prv_segment.isin(roads.index)
        & match_points.nxt_segment.isin(roads.index)
    )

    match_points.loc[mask, "segment"] = match_points.loc[mask].apply(
        lambda x: get_closest_roads_id(
            x.geometry,
            roads.loc[x.prv_segment, "geometry"],
            roads.loc[x.nxt_segment, "geometry"],
            x["prv_segment"],
            x["nxt_segment"],
        ),
        axis=1,
    )

    return match_points


def parse_valhalla_trace_attribues(res):
    """_summary_

    Parameters
    ----------
    res : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """

    match_points = pd.DataFrame(res["matched_points"])
    #Valhalla overflow on edge_index, see mapmatch.mapmatch
    match_points.loc[match_points.edge_index > 30000000, 'edge_index'] = np.nan
    edges = pd.DataFrame(res["edges"])
    edges.index = edges.index.astype(np.float64)
    match_points = match_points.join(edges, on=["edge_index"], how="left")
    match_points = gpd.GeoDataFrame(
        match_points,
        geometry=gpd.points_from_xy(match_points.lon, match_points.lat),
        crs="epsg:4326",
    )

    match_points.rename(
        columns={
            "lat": "lat_match",
            "lon": "lng_match",
            "distance_along_edge": "point_on_segment",
            "way_id": "segment",
        },
        inplace=True,
    )

    return match_points


def osrm_parse_matchs(response):
    """_summary_

    Parameters
    ----------
    response : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """

    ### Retrieve match points
    # create an empty response
    empty_response = {
        "location": [0, 0],
        "name": None,
        "hint": None,
        "matchings_index": None,
        "waypoint_index": None,
        "alternatives_count": None,
    }
    # create list of matchs
    tracepoints = [
        x if x is not None else empty_response for x in response["tracepoints"]
    ]
    # create a DataFrame of matchs
    res = pd.DataFrame.from_records(tracepoints)

    return res


def osrm_parse_legs(response):
    """_summary_

    Parameters
    ----------
    response : _type_
        _description_
    gdf_edges : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    ### retrieve each edge on match_points
    legs_df = pd.DataFrame(columns=["matchings_index", "waypoint_index", "u", "v"])
    for i, matching in enumerate(response["matchings"]):
        for j, leg in enumerate(matching["legs"]):
            u = leg["annotation"]["nodes"][0]
            v = leg["annotation"]["nodes"][1]
            leg_i = j
            # append new row
            legs_df.loc[-1] = [i, leg_i, u, v]  # adding a row
            legs_df.index = legs_df.index + 1  # shifting index
            legs_df = legs_df.sort_index()  # sorting by index

            if (
                j == len(matching["legs"]) - 1
            ):  # on est au dernier point, il faut l'ajouter aussi
                u = leg["annotation"]["nodes"][-2]
                v = leg["annotation"]["nodes"][-1]
                leg_i = j + 1
                # append last point
                legs_df.loc[-1] = [i, leg_i, u, v]  # adding a row
                legs_df.index = legs_df.index + 1  # shifting index
                legs_df = legs_df.sort_index()  # sorting by index

    # legs_df = legs_df.merge(gdf_edges, on=['u','v'], how='inner')
    legs_df = legs_df[["matchings_index", "waypoint_index", "u", "v"]]  # , 'osmid']]

    # remove potential duplicate edges
    # legs_df = legs_df.loc[legs_df[['matchings_index', 'waypoint_index', 'u', 'v']].drop_duplicates(keep='first').index]

    return legs_df


def osrm_parse_response(response):
    """_summary_

    Parameters
    ----------
    response : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """

    matchs = osrm_parse_matchs(response)

    # format location
    locations = np.stack(matchs["location"], axis=0)
    matchs["lng_match"] = locations[:, 0]
    matchs["lat_match"] = locations[:, 1]

    return matchs[OSRM_MATCH_COLUMNS]


class MapMatcher:
    """_summary_"""

    _supported_client = ["OSRM", "Valhalla"]

    def __init__(self, host, engine="osrm", **kwargs):

        self.engine = engine
        self.host = host
        self.client = None
        self.columns = []
        self._parameters = kwargs

        self._start_client(**kwargs)

    def _start_client(self, **kwargs):
        client = None
        if self.engine == "osrm":
            client = osrm.Client(self.host, timeout=60, **kwargs)
        elif self.engine == "valhalla":
            # TODO: set the right instance here ?
            client = "HTTP API"
        self._check_client(client)

    def _check_client(self, client):
        if isinstance(client, osrm.Client):
            self.client = client
            self.columns = OSRM_MATCH_COLUMNS
        elif isinstance(client, str):
            self.client = client
            self.columns = VALHALLA_MATCH_COLUMNS
        else:
            raise TypeError(
                "MapMatcher constructor called with incompatible client and dtype: {e}".format(
                    e=type(client)
                )
            )

    @classmethod
    def supported_client(cls):
        """_summary_

        Returns
        -------
        _type_
            _description_
        """
        return cls._supported_client

    def match(self, coords, **kwargs):
        """Perform matching based on the client specified.

        Parameters
        ----------
        coords : _type_
            _description_

        Returns
        -------
        _type_
            _description_

        Raises
        ------
        NotImplementedError
            _description_
        """
        if self.client is None:
            self._start_client()

        if self.engine == "osrm":
            data = self._osrm_match(coords, **kwargs)

        elif self.engine == "valhalla":
            costing = kwargs.pop("costing", "auto")
            shape_match = kwargs.pop("shape_match", "map_snap")
            data = self._valhalla_match(
                coords, costing=costing, shape_match=shape_match, **kwargs
            )
        else:
            raise NotImplementedError("There is no implementation for this matcher")

        # FIXME this will fail when object is not pythonic (e.g. dataframe)
        if kwargs.get("index", None):
            data["data_index"] = kwargs.get("index")

        return data

    def _osrm_match(self, coords, **kwargs):
        """Coords is in format lat, lng np.array"""

        coords = np.asarray(coords)
        assert coords.ndim == 2, "Coordinates should be 2 dimensions"

        if "timestamps" in kwargs:
            kwargs["timestamps"] = list(kwargs["timestamps"])

        try:
            response = self.client.match(
                coordinates=coords[:, ::-1],
                overview=osrm.overview.full,
                annotations=True,
                **kwargs,
            )
            if response["code"] != "Ok":
                return pd.DataFrame()
        except osrm.OSRMClientException as e:
            logging.error(f"Error happened when mapmatching : {e}")
            return pd.DataFrame()

        # retrieve paresed matchs
        matchs = osrm_parse_response(response)
        matchs = matchs.rename(columns=OSRM_2_MATCHER)

        # concat with ori points
        assert (
            matchs.shape[0] == coords.shape[0]
        ), f"Something went wrong during map matching: match shape {matchs.shape[0]} != coords shape {coords.shape[0]}"

        return matchs

    def _valhalla_match(self, coords, costing, shape_match, **kwargs):
        """_summary_

        Parameters
        ----------
        tdf : TrajDataFrame
            _description_
        costing : str, optional
            _description_, by default 'auto'
        shape_match : str, optional
            _description_, by default 'map_snap'

        Returns
        -------
        _type_
            _description_
        """

        kwargs.update({"filters": VALHALLA_FILTERS})
        kwargs.update({"format": "osrm"})
        kwargs.update({"trace_options": {"search_radius": 20}})
        payload = create_valhalla_payload(coords, costing, shape_match, **kwargs)

        response = requests.post(
            url=self.host + "/trace_attributes",
            data=json.dumps(payload, cls=NpEncoder),
            timeout=120,
        )

        logger.debug(
            "Code %s - Number of cooords %s", response.status_code, coords.shape[0]
        )
        if response.status_code == 200:
            match_dict = response.json()
            match_points = parse_valhalla_trace_attribues(match_dict)
            columns = np.intersect1d(self.columns, match_points.columns)

            return match_points[columns]

        logger.error("%s: %s", response.status_code, response.text)

        return pd.DataFrame(np.NaN, np.arange(len(coords)), columns=self.columns)

    def post_process_matching(self, match_points, roads):
        """_summary_

        Parameters
        ----------
        match_points : _type_
            _description_
        roads : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """

        match_points = gpd.GeoDataFrame(
            data=match_points,
            geometry=gpd.points_from_xy(match_points.lng_match, match_points.lat_match),
            crs="epsg:4326",
        )
        if self.engine == "valhalla":
            match_points = match_points.sort_values(
                [constants.UUID, constants.DATETIME]
            )
            match_points = infer_interpolated_way_id(roads, match_points)
            match_points = match_points.sort_values(constants.DATETIME)
        else:
            logger.info("Nothing to do")

        match_points.drop(columns="geometry", inplace=True)
        return match_points
