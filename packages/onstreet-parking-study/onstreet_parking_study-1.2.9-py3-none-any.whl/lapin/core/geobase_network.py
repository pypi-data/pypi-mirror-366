""" Road Network data """

from typing import Callable, cast

import pandas as pd
import geopandas as gpd
import networkx as nx

from lapin import constants
from lapin.io.load import data_from_conf
from lapin.io.sql import get_engine
from lapin.io.types import EngineConfig
from lapin.configs.mtl_opendata import ROADS_CONNECTION_MTL, ROADS_DB_CONNECTION_MTL
from lapin.tools.graph import (
    construct_graph,
    convert_geobase_to_osmnx,
    get_segment_intersection_name,
)
from lapin.core._utils import create_network_config


class RoadNetworkSeries(pd.Series):
    """Serie"""

    @property
    def _constructor(self):
        return RoadNetworkSeries

    @property
    def _constructor_expanddim(self):
        return RoadNetwork


class BaseRoadNetwork(object):
    """Metaclass for RoadNetwork and RoadNetworkDouble"""

    @property
    def graph(self) -> nx.MultiGraph:
        """Construct a graph from a RoadNetwork.

        Returns
        -------
        nx.MultiGraph

        Raises
        ------
        NotImplementedError
            Cannot create a graph from RoadNetworkDouble
        """
        if isinstance(self, RoadNetworkDouble):
            raise NotImplementedError("Cannot construct graph for RoadNetworkDouble.")
        return construct_graph(self, crs=self.crs)

    @property
    def osm_graph(self) -> nx.MultiGraph:
        """Export RoadNetwork to OSM graph.

        Returns
        -------
        nx.MultiGraph

        Raises
        ------
        NotImplementedError
            Cannot create a graph from RoadNetworkDouble
        """
        if isinstance(self, RoadNetworkDouble):
            raise NotImplementedError("Cannot construct graph for RoadNetworkDouble.")
        return convert_geobase_to_osmnx(self, traffic_dir=True)

    @property
    def human_readable(self):
        """Add columns constantas.FROM_ROADS, constantsTO_ROADS and
        constants.ROAD_NAME to the RoadNetwork.

        Returns
        -------
        RoadNetwork

        Raises
        ------
        NotImplementedError
            Cannot create a graph from RoadNetworkDouble
        """
        if isinstance(self, RoadNetworkDouble):
            raise NotImplementedError("Cannot construct graph for RoadNetworkDouble.")
        graph = self.graph
        data = self.copy()

        data[constants.HR_ROAD_NAME] = data[constants.ROAD_NAME].copy()
        data[constants.HR_FROM_ROAD] = data.apply(
            lambda x: get_segment_intersection_name(
                graph=graph,
                seg_id=x[constants.SEGMENT],
                seg_col=constants.SEGMENT,
                col_name=constants.ROAD_NAME,
            )[0],
            axis=1,
        )
        data[constants.HR_TO_ROAD] = data.apply(
            lambda x: get_segment_intersection_name(
                graph=graph,
                seg_id=x[constants.SEGMENT],
                seg_col=constants.SEGMENT,
                col_name=constants.ROAD_NAME,
            )[1],
            axis=1,
        )

        columns = [
            constants.HR_ROAD_NAME,
            constants.HR_FROM_ROAD,
            constants.HR_TO_ROAD,
            constants.SEGMENT,
            constants.GEOMETRY,
        ]
        return data[columns]

    def create_network_config(
        self, uuid_list: list[str], desagregated_street_name: list[str]
    ) -> pd.DataFrame:
        """Create a roadnetwork configuration data for the study.

        Parameters
        ----------
        uuid_list : list[str]
            List of uuid to consider.
        desagregated_street_name : list[str]
            Street where to keep sides desagregated.

        Returns
        -------
        pd.DataFrame
            Network configuration.
        """

        return create_network_config(
            roads=self,
            uuid_list=uuid_list,
            desagregated_street=desagregated_street_name,
        )


class RoadNetwork(BaseRoadNetwork, gpd.GeoDataFrame):
    """RoadNetwork Goemetry"""

    def __init__(
        self,
        data: gpd.GeoDataFrame,
        *args,
        id_: str = constants.SEGMENT,
        road_name: str = constants.ROAD_NAME,
        traffic_dir: str = constants.TRAFFIC_DIR,
        version: str | None = None,
        **kwargs,
    ):
        """FIXME: Short description.

        FIXME: Long description.

        Parameters
        ----------
        data : gpd.GeoDataFrame
            FIXME: Add docs.
        id_ : str
            FIXME: Add docs.
        road_name : str
            FIXME: Add docs.
        traffic_dir : str
            FIXME: Add docs.

        Examples
        --------
        FIXME: Add docs.

        """
        super().__init__(data, *args, **kwargs)

        original2default = {
            id_: constants.SEGMENT,
            road_name: constants.ROAD_NAME,
            traffic_dir: constants.TRAFFIC_DIR,
        }

        self.rename(columns=original2default, inplace=True)

        if version:
            self["version"] = version

    def _has_rn_columns(self):

        if (
            (constants.SEGMENT in self)
            and (constants.ROAD_NAME in self)
            and (constants.TRAFFIC_DIR in self)
        ):
            return True

        return False

    def _is_roadnetwork(self):
        if (
            self._has_rn_columns()
            and (pd.core.dtypes.common.is_integer_dtype(self[constants.SEGMENT]))
            and (pd.core.dtypes.common.is_string_dtype(self[constants.ROAD_NAME]))
            and (pd.core.dtypes.common.is_integer_dtype(self[constants.TRAFFIC_DIR]))
        ):
            return True

        return False

    def __getitem__(self, key):
        """If the result contains traffic_dir, road_name and ID return a
        RoadNetwork, else a geopandas GeoDataFrame.
        """
        result = super().__getitem__(key)
        old_class = result.__class__

        result.__class__ = RoadNetwork
        if not result._is_roadnetwork():
            result.__class__ = old_class

        return result

    def copy(self, deep=True):
        """FIXME: Short description.

        FIXME: Long description.

        Parameters
        ----------
        deep : FIXME: Add type.
            FIXME: Add docs.

        Examples
        --------
        FIXME: Add docs.

        """
        copied = super().copy(deep=deep)
        if isinstance(copied, gpd.GeoDataFrame):
            copied.__class__ = RoadNetwork
        return copied

    @property
    def _constructor(self):
        return RoadNetwork

    @property
    def _constructor_sliced(self):
        return RoadNetworkSeries

    @property
    def _constructor_expanddim(self):
        return RoadNetwork

    def _slice(self, *args, **kwargs):
        result = super()._slice(*args, **kwargs)
        return self._constructor(result)

    def take(self, *args, **kwargs):
        """FIXME: Short description.

        FIXME: Long description.

        Examples
        --------
        FIXME: Add docs.

        """
        result = super().take(*args, **kwargs)
        return self._constructor(result)

    def _reindex_with_indexers(self, *args, **kwargs):
        result = super()._reindex_with_indexers(*args, **kwargs)
        return self._constructor(result)

    @classmethod
    def load_geobase_from_mtl_open_data(cls, config=ROADS_CONNECTION_MTL):
        """Read geobase from Montreal Open Data

        Returns
        -------
        RoadNetwork
        """
        data = data_from_conf(config)
        data = data.to_crs("epsg:4326")

        return cls(
            data,
            id_=constants.SEG_DB_ID,
            road_name=constants.SEG_DB_STREET,
            traffic_dir="SENS_CIR",
        )

    @classmethod
    def from_postgres(
        cls,
        engine_conf: EngineConfig,
        schema: str,
        table: str,
        version: str | None = None,
        columns_config: dict | None = None,
    ):

        engine = get_engine(**engine_conf)
        query_sql = f"""
            select
             t.*,
            from {schema}.{table} t
            """
        if version:
            query_sql += f"where version = {version}"
        else:
            query_sql += "where curr_vers = True"

        df = gpd.read_postgis(con=engine, sql=query_sql)

        df = gpd.GeoDataFrame(df, geometry="geom")
        df = df.rename_geometry("geometry")
        df = cast(gpd.GeoDataFrame, df)

        if columns_config:
            return cls(df, **columns_config)
        else:
            return cls(df)

    @classmethod
    def load_geobase_from_curbsnap(
        cls,
        projects_list: list[str] | None = None,
        version: int | None = None,
        func: Callable | None = None,
    ):
        """Load geobase from Curbsnap

        Returns
        -------
        RoadNetwork
        """
        if version is None and projects_list is None:
            raise ValueError("One of project_list or version must be specified.")

        config = {
            "type": "curbsnapp",
            "config": {"projects_list": projects_list, "geobase_type": "simple"},
            "post_processing": bool(func),
            "func": func,
        }
        if version:
            config = {
                "type": "curbsnapp_geobase",
                "config": {"version": version, "geobase_type": "simple"},
                "post_processing": bool(func),
                "func": func,
            }

        data, versions = data_from_conf(config)
        if isinstance(versions, list) and len(set(versions)) > 1:
            raise NotImplementedError(
                "Several geobases version or None is not supported. Please see with your curbsnapp admin."
            )

        if isinstance(versions, list):
            versions = versions[0]

        data = data.to_crs("epsg:4326")

        return cls(
            data,
            id_="ID_TRC",
            road_name="NOM_VOIE",
            traffic_dir="SENS_CIR",
            version=versions,
        )


class RoadNetworkDouble(BaseRoadNetwork, gpd.GeoDataFrame):
    """RoadNetworkDouble Goemetry"""

    def __init__(
        self,
        data: gpd.GeoDataFrame,
        *args,
        id_: str = constants.SEGMENT,
        road_name: str = constants.ROAD_NAME,
        traffic_dir: str = constants.TRAFFIC_DIR,
        side_of_street: str = constants.SIDE_OF_STREET,
        version: str | None = None,
        **kwargs,
    ):

        super().__init__(data, *args, **kwargs)

        original2default = {
            id_: constants.SEGMENT,
            road_name: constants.ROAD_NAME,
            traffic_dir: constants.TRAFFIC_DIR,
            side_of_street: constants.SIDE_OF_STREET,
        }

        self.rename(columns=original2default, inplace=True)

        # # Rename geometry
        if (
            isinstance(self, gpd.GeoDataFrame)
            and constants.SEG_DB_GIS not in self
            and self._geometry_column_name is not None
        ):
            self.rename_geometry(constants.SEG_DB_GIS, inplace=True)

        if version:
            self["version"] = version

    def _has_rn_columns(self):

        if (
            (constants.SEGMENT in self)
            and (constants.ROAD_NAME in self)
            and (constants.TRAFFIC_DIR in self)
            and (constants.SIDE_OF_STREET in self)
        ):
            return True

        return False

    def _is_roadnetwork(self):
        if (
            self._has_rn_columns()
            and (pd.core.dtypes.common.is_integer_dtype(self[constants.SEGMENT]))
            and (pd.core.dtypes.common.is_string_dtype(self[constants.ROAD_NAME]))
            and (pd.core.dtypes.common.is_integer_dtype(self[constants.TRAFFIC_DIR]))
            and (pd.core.dtypes.common.is_integer_dtype(self[constants.SIDE_OF_STREET]))
        ):
            return True

        return False

    def __getitem__(self, key):
        """
        If the result contains lat, lng and datetime, return a TrajDataFrame,
        else a pandas DataFrame.
        """
        result = super().__getitem__(key)
        old_class = result.__class__

        result.__class__ = RoadNetworkDouble
        if not result._is_roadnetwork() or constants.SEG_DB_GIS not in result:
            result.__class__ = old_class

        return result

    @property
    def _constructor(self):
        return RoadNetworkDouble

    @property
    def _constructor_sliced(self):
        return RoadNetworkSeries

    @property
    def _constructor_expanddim(self):
        return RoadNetworkDouble

    def _slice(self, *args, **kwargs):
        result = super()._slice(*args, **kwargs)
        return self._constructor(result)

    def take(self, *args, **kwargs):
        result = super().take(*args, **kwargs)
        return self._constructor(result)

    def _reindex_with_indexers(self, *args, **kwargs):
        result = super()._reindex_with_indexers(*args, **kwargs)
        return self._constructor(result)

    def copy(self, deep=True):
        copied = super().copy(deep=deep)
        if isinstance(copied, gpd.GeoDataFrame):
            copied.__class__ = RoadNetworkDouble
        return copied

    @classmethod
    def load_geobase_from_mtl_open_data(cls):
        """Read geobase from Montreal Open Data

        Returns
        -------
        RoadNetwork
        """
        data = data_from_conf(ROADS_DB_CONNECTION_MTL)
        data = data.to_crs("epsg:4326")

        return cls(
            data,
            id_=constants.SEGMENT,
            road_name=constants.ROAD_NAME,
            traffic_dir=constants.TRAFFIC_DIR,
            side_of_street=constants.SIDE_OF_STREET,
        )

    @classmethod
    def from_postgres(
        cls,
        engine_conf: EngineConfig,
        schema: str,
        table: str,
        version: str | None = None,
        columns_config: dict | None = None,
    ):

        engine = get_engine(**engine_conf)
        query_sql = f"""
            select
             t.*,
            from {schema}.{table} t
            """
        if version:
            query_sql += f"where version = {version}"
        else:
            query_sql += "where curr_vers = True"

        df = gpd.read_postgis(con=engine, sql=query_sql)

        df = gpd.GeoDataFrame(df, geometry="geom")
        df = df.rename_geometry("geometry")
        df = cast(gpd.GeoDataFrame, df)

        df["cote_rue"] = df["cote"].map(constants.SEG_DB_SIDE_OF_STREET_MAP)

        if columns_config:
            return cls(df, **columns_config)
        else:
            return cls(df)

    @classmethod
    def load_geobase_from_curbsnap(
        cls,
        projects_list: list[str] | None = None,
        version: int | None = None,
        func: Callable | None = None,
    ):
        """Load geobase from Curbsnap

        Returns
        -------
        RoadNetwork
        """
        if version is None and projects_list is None:
            raise ValueError("One of project_list or version must be specified.")

        config = {
            "type": "curbsnapp",
            "config": {"projects_list": projects_list, "geobase_type": "double"},
            "post_processing": bool(func),
            "func": func,
        }
        if version:
            config = {
                "type": "curbsnapp_geobase",
                "config": {"version": version, "geobase_type": "double"},
                "post_processing": bool(func),
                "func": func,
            }
        data, versions = data_from_conf(config)
        if isinstance(versions, list) and len(set(versions)) > 1:
            raise NotImplementedError(
                "Several geobases version or None is not supported. Please see with your curbsnapp admin."
            )

        if isinstance(versions, list):
            versions = versions[0]

        data[constants.SEG_DB_SIDE] = (data[constants.SEG_DB_ID_SIDE] % 10).values
        data[constants.SEG_DB_SIDE] = data[constants.SEG_DB_SIDE].map(
            {1: "Droite", 2: "Gauche"}
        )
        data["COTE_RUE"] = data[constants.SEG_DB_SIDE].map(
            constants.SEG_DB_SIDE_OF_STREET_MAP
        )
        data = data.to_crs("epsg:4326")

        return cls(
            data,
            id_="ID_TRC",
            road_name="NOM_VOIE",
            traffic_dir="SENS_CIR",
            side_of_street="COTE_RUE",
            version=versions,
        )


def _dataframe_set_roadnetwork(self, col, drop=False, inplace=False, crs=None):
    if inplace:
        raise ValueError(
            "Can't do inplace setting when converting from"
            + " DataFrame to GeoDataFrame"
        )
    gf = RoadNetwork(self)

    # this will copy so that BlockManager gets copied
    return gf._set_roadnetwork(col, drop=drop, inplace=False, crs=crs)


pd.DataFrame._set_roadnetwork = _dataframe_set_roadnetwork
