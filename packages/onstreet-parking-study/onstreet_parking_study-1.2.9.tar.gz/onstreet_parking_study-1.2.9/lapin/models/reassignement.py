"""Module to modelize report of parking on other streets

"""
import logging
import momepy

import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx

from lapin.tools.graph import construct_graph
from lapin import constants

logger = logging.getLogger(__name__)


def modelize_reassignement_graph(
    graph: (gpd.GeoDataFrame | nx.Graph),
    index_name='ID_TRC'
) -> nx.Graph:
    """_summary_

    Parameters
    ----------
    graph : gpd.GeoDataFrame  |  nx.Graph
        _description_
    index_name : str, optional
        _description_, by default 'ID_TRC'

    Returns
    -------
    nx.Graph
        _description_
    """

    if isinstance(graph, gpd.GeoDataFrame):
        graph = construct_graph(graph, limits=None, crs='epsg:32188')
    nodes, edges = momepy.nx_to_gdf(graph)

    # Rename nodes name
    nodes['node_label'] = nodes.geometry.apply(lambda x: (x.x, x.y))
    node_mapping_rename = nodes.set_index('node_label')['nodeID'].to_dict()
    gg = nx.Graph(nx.relabel_nodes(graph, node_mapping_rename))

    # roads are nodes, edge are connectivity
    new_graph = nx.line_graph(gg, create_using=nx.Graph)

    # Rename edges to match idx_roads
    edges['edge_label'] = edges[['node_start', 'node_end']].apply(
        lambda x: (x.node_start, x.node_end), axis=1
    )
    edges_mapping_rename = edges.set_index('edge_label')[index_name].to_dict()
    new_graph = nx.relabel_nodes(G=new_graph, mapping=edges_mapping_rename)

    # distance bewteen roads
    for ((n1, n2), _) in new_graph.edges.items():
        new_graph[n1][n2]['weight'] = (edges.loc[edges[index_name] == n1,
                                                 'mm_len'].values[0] +
                                       edges.loc[edges[index_name] == n2,
                                                 'mm_len'].values[0]) / 2

    return new_graph


def prepare_data(
    cap: pd.DataFrame,
    veh: pd.DataFrame,
    hours: list
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """_summary_

    Parameters
    ----------
    cap : pd.DataFrame
        _description_
    veh : pd.DataFrame
        _description_
    hours : list
        _description_

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        _description_
    """

    cap = cap.copy()
    veh = veh.copy()

    cap = cap[hours]
    veh = veh[hours]

    cols_agg = {col: 'sum'
                for col in cap.columns
                if col != constants.SEG_DB_GIS}

    cap = cap.groupby('segment').agg(cols_agg)
    veh = veh.groupby('segment').agg(cols_agg)

    return cap, veh


class SpotReassignement():
    """Report modelisation class

    Parameters
    ----------
    graph : nx.Graph
        Road network
    road_ids : list[int]
        Roads Id to replace
    """

    def __init__(self, graph: nx.Graph, road_ids: list[int]):
        """_summary_

        Parameters
        ----------
        graph : nx.Graph
            _description_
        road_ids : list[int]
            _description_
        """
        self.graph = graph
        self.road_ids = road_ids

        self._idx_name = 'segment'

    @classmethod
    def from_geobase(
        cls,
        geobase: gpd.GeoDataFrame,
        road_name: list[str] | str,
        idx_name: str = 'ID_TRC',
        col_road_name: str = 'NOM_VOIE'
    ):
        """_summary_

        Parameters
        ----------
        geobase : gpd.GeoDataFrame
            _description_
        road_name : list[str] | str
            _description_
        idx_name : str, optional
            _description_, by default 'ID_TRC'
        col_road_name : str, optional
            _description_, by default 'NOM_VOIE'

        Returns
        -------
        _type_
            _description_
        """
        graph = modelize_reassignement_graph(geobase, idx_name)

        if isinstance(road_name, list):
            road_ids = geobase.loc[
                geobase[col_road_name].isin(road_name), idx_name
            ].unique()
        else:
            road_ids = geobase.loc[
                geobase[col_road_name] == road_name, idx_name
            ].unique()

        if len(road_ids) == 0:
            return -1

        return cls(graph, road_ids)

    def reassign_on_nearby_street(
        self,
        cap: pd.Series,
        veh: pd.Series,
        search_radius: int = 500
    ) -> tuple[pd.Series, list]:
        """ Return the estimated capacity once every parking events on the
        street to remove have been move to adjacent streets.

        Parameters
        ----------
        cap: pd.Series
            Capacity of each street. Index by road_id.
        veh: pd.Series
            Parking events on each street. Index by road_id
        search_radius: int, optional
            Search radius in meters to quantify available nearby street.
            Default is 500.

        Returns
        -------
        reserv_capacity: pd.Series
            Capacity left on streets after moving veh on self.road_ids onto
            nearby streets.
        problematic_roads: list
            List of street's parking events that cannot be assigned to adjacent
            streets.
        """

        # recover id of roads
        rm_roads_id = np.intersect1d(self.road_ids, cap.index)
        nearby_roads_id = cap.index[~cap.index.isin(rm_roads_id)]

        # remove existant parking needs from nearby street's capacity
        reserv_capacity = cap.copy()
        veh_nearby_st = veh.copy()
        reserv_capacity.loc[rm_roads_id] = 0
        veh_nearby_st.loc[rm_roads_id] = 0
        reserv_capacity -= veh_nearby_st

        problematic_roads = []
        distance_deplacement = {}
        for road in rm_roads_id:
            distance_deplacement[road] = {}

            # ego graph at radius
            try:
                ego_graph = nx.ego_graph(
                    self.graph,
                    road,
                    radius=search_radius,
                    distance='weight'
                )
            except nx.exception.NodeNotFound:
                continue

            # distance
            near_roads_dist = dict(
                nx.all_pairs_dijkstra_path_length(ego_graph, weight='weight')
            )

            # nodes in the ego graph sort by dist
            near_roads = ego_graph.nodes
            near_roads = np.intersect1d(near_roads, nearby_roads_id)

            near_roads = sorted(
                near_roads,
                key=lambda x: near_roads_dist[road][x]
            )

            to_deplace = veh.loc[road]
            if len(near_roads) == 0:
                continue
            i = 0
            while to_deplace > 0:
                road_avail = near_roads[i]
                movable = min(reserv_capacity.loc[road_avail], to_deplace)

                if movable <= 0 and i < len(near_roads)-1:
                    i += 1
                    continue
                if i == len(near_roads)-1:
                    if to_deplace > movable:
                        problematic_roads.append(road)
                        logger.info('Cannot re-assign veh on road %s', road)
                        logger.info('Default road used %s', road_avail)
                        logger.info('Roads near by %s', near_roads)

                    movable = to_deplace

                distance_deplacement[road]['nb_veh'] = to_deplace
                distance_deplacement[road]['distance_depl'] = (
                    near_roads_dist[road][road_avail]
                )
                to_deplace -= movable
                reserv_capacity.loc[road_avail] -= movable

                i += 1

        return reserv_capacity, distance_deplacement, problematic_roads

    def compute_hr_reassignement(
        self,
        cap: pd.DataFrame,
        veh: pd.DataFrame,
        hours: list,
        search_radius: int = 500
    ) -> tuple[pd.DataFrame, dict, dict, list, list]:
        """Compute vehicule reassignement for each hour.

        Paramaters
        ----------
            cap: pd.DataFrame
                Street parking capacity, each columns represent one hour.
            veh: pd.DataFrame
                Occurence of parking on streets. Each columns represent one
                hour.
            hours: list
                List of hours to compute the reassignement.

        Returns
        -------
        df: pd.DataFrame
            Capacity, parkign occurance, reserv_capacity and
            max_reserve_capacity aggregated at street level. By hour.
        dist_reassignement: dict
            For each road reassigned, get the distance of the reassignement.
        dist_reassignement_max: dict
            For each road reassigned at maximum capacity, get the distance of
            the reassignement.
        problematic_street: 2d list
            Index of street where parking occurence could not be moved to
            adjacent street. Indicate that there is not enough parking spot
            near those street.
        max_problematic_street: 2d list
            Index of street where maximum parking occurence could not be moved
            to adjacent street. Indicate that there is not enough parking spot
            near those street.

        See Also
        --------
        reasign_on_nearby_street : core computation of reassignement.
        """
        # aggregate to street level (instead of side_of_street)
        cap, veh = prepare_data(cap, veh, hours)

        # modelize parked vehicule as max capacity
        vehmax = veh.copy()
        idx = np.intersect1d(self.road_ids, vehmax.index)
        vehmax.loc[idx] = cap.loc[idx]

        result_1 = []
        dist_1 = []
        pb_1 = []
        result_2 = []
        dist_2 = []
        pb_2 = []
        for col in hours:
            veh.loc[(cap[col] - veh[col]) < 0, col] = cap.loc[
                (cap[col] - veh[col]) < 0,
                col
            ]
            vehmax.loc[(cap[col] - vehmax[col]) < 0, col] = cap.loc[
                (cap[col] - vehmax[col]) < 0,
                col
            ]

            # Vehicule reassignement
            caphr, dist, road_pb = self.reassign_on_nearby_street(
                cap=cap[col],
                veh=veh[col],
                search_radius=search_radius
            )
            result_1.append(caphr)
            dist_1.append(dist)
            pb_1.append(road_pb)

            # Max capacity reassignement
            caphr_max, dist_max, road_pb_max = self.reassign_on_nearby_street(
                cap=cap[col],
                veh=vehmax[col],
                search_radius=search_radius
            )
            result_2.append(caphr_max)
            dist_2.append(dist_max)
            pb_2.append(road_pb_max)

        df = self.prettyfy(
            cap,
            veh,
            pd.concat(result_1, axis=1),
            pd.concat(result_2, axis=1)
        )
        return df, dist_1, dist_2, pb_1, pb_2

    def prettyfy(
        self,
        cap: pd.DataFrame,
        veh: pd.DataFrame,
        cap_reassign: pd.DataFrame,
        cap_max_reassing: pd.DataFrame
    ) -> pd.DataFrame:
        """ Human readable way to read the reassignement.

        Parameters
        ----------
        cap: pd.DataFrame
            Street capacity. Indexed by stret id.
        veh: pd.DataFrame
            Parking occurences on street. Indexed by street id.
        cap_reassign: pd.DataFrame
            Resulting street capacity after reassignement. Indexed by street
            id.
        cap_max_reassign: pd.DataFrame
            Resulting street capacity after maximum reassignement. Indexed by
            street id.

        Returns
        -------
        pd.DataFrame
            Reassignement as a table>
        """
        cap = cap.copy()\
            .reset_index()\
            .melt(
                id_vars=self._idx_name,
                value_name='capacity',
                var_name='hour'
            )\
            .set_index([self._idx_name, 'hour'])
        veh = veh.copy()\
            .reset_index()\
            .melt(
                id_vars=self._idx_name,
                value_name='parking_occurences',
                var_name='hour'
            )\
            .set_index([self._idx_name, 'hour'])
        cap_reassign = cap_reassign.copy()\
            .reset_index()\
            .melt(
                id_vars=self._idx_name,
                value_name='avg_free_parking_spot',
                var_name='hour'
            )\
            .set_index([self._idx_name, 'hour'])
        cap_max_reassing = cap_max_reassing.copy()\
            .reset_index()\
            .melt(
                id_vars=self._idx_name,
                value_name='min_free_parking_spot',
                var_name='hour'
            )\
            .set_index([self._idx_name, 'hour'])

        return pd.concat([cap, veh, cap_reassign, cap_max_reassing], axis=1)
