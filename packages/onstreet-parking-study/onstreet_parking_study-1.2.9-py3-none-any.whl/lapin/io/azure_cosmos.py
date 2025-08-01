""" This module provide utils for connecting to an azure cosmos database
and making read operation. """

import copy
import re
import json
from typing import List
import logging
from datetime import datetime, timezone, timedelta

import azure
import azure.cosmos
import azure.cosmos.cosmos_client as cosmos_client
import pandas as pd
import geopandas as gpd

from lapin.constants import PROJECT_TIMEZONE

logger = logging.getLogger(__name__)

LOCAL_TZNAME = PROJECT_TIMEZONE


def cosmos_geom_to_geojson(cosmos_geom: list) -> dict:
    """_summary_

    Parameters
    ----------
    cosmos_geom : list
        Result of a query to a geographic cosmos container

    Returns
    -------
    dict

    """
    geojson = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        },
        "features": cosmos_geom,
    }

    return geojson


def parse_dates(
    dates: List[dict[str, str]], date_only: bool = True, to_string: bool = True
) -> List[dict[str, str]]:
    """_summary_

    Parameters
    ----------
    dates : List[dict[str, str]]
        _description_
    date_only : bool, optional
        _description_, by default True

    Returns
    -------
    List[dict[str, str]]
        _description_
    """

    dates = copy.deepcopy(dates)

    for date in dates:
        from_d = datetime.fromisoformat(date["from"])
        to_d = datetime.fromisoformat(date["to"])

        from_d = from_d.astimezone()
        to_d = to_d.astimezone()
        to_d += timedelta(hours=23, minutes=59, seconds=59)

        if date_only:
            from_d_utc = from_d.astimezone(timezone.utc).date()
            to_d_utc = to_d.astimezone(timezone.utc).date()
            format_dt = "%Y-%m-%d"

        else:
            from_d_utc = from_d.astimezone(timezone.utc)
            to_d_utc = to_d.astimezone(timezone.utc)
            format_dt = "%Y-%m-%d %H:%M:%S"

        if to_string:
            date["from"] = from_d_utc.strftime(format_dt)
            date["to"] = to_d_utc.strftime(format_dt)
        else:
            date["from"] = from_d_utc
            date["to"] = to_d_utc

    return dates


def query_between_dates(
    container: azure.cosmos.container.ContainerProxy,
    dates: List[dict],
    query: str,
    date_col: str = "date",
    cross_partition=False,
) -> List[dict]:
    """
    Parameters
    ----------
    container: azure.cosmos.container.ContainerProxy
        Azure container to query
    dates: List[dict]
        List of date_range to query. Date range are dict with keys `from`,
        `to`.
    query: str
        String query.
    date_col: str, optional
        Date column for the container. Default='date'
    cross_partition: bool, optional
        Allow cross partition query. Default=False

    Returns
    -------
    list
        iterable of all items
    """

    if re.search("where", query, re.IGNORECASE):
        query += " AND "
    else:
        query += "WHERE"

    dates = parse_dates(dates, True, True)

    where_cond = " ("
    for date in dates:
        where_cond += (
            f"c.{date_col} >= \"{date['from']}\""
            + f" AND c.{date_col} <= \"{date['to']}\""
        )
        where_cond += " OR "

    where_cond += " 1=2)"

    query += where_cond

    logger.debug("Query executed on azre : %s", query)

    # querry
    res_query = container.query_items(
        query=query, enable_cross_partition_query=cross_partition
    )

    return list(res_query)


def query_container(
    container: azure.cosmos.container.ContainerProxy, query: str, cross_partitions=False
) -> List[dict]:
    """_summary_

    Parameters
    ----------
    container : azure.cosmos.container.ContainerProxy
        _description_
    query : str
        _description_
    cross_partitions : bool, optional
        _description_, by default False

    Returns
    -------
    _type_
        _description_
    """
    # querry
    res_query = container.query_items(
        query=query, enable_cross_partition_query=cross_partitions
    )

    return list(res_query)


def cosmos_db_to_geodataframe(
    query: str, cosmos_config: dict, dates: list = None, **kwargs
) -> gpd.GeoDataFrame:
    """Query a cosmos db container and load it into a pandas geodataframe

    Parameters
    ----------
    query : str
        query, with or without where clause.
    cosmos_config : dict, optional
        Connection setting for cosmos database, by default
        config.cosmos_settings
    dates : list[dicts[str, str]], optional
        Date config for querying only selected dates, by default None
    kwargs
        Accepted key is enable_cross_partition_querry (bool)

    Returns
    -------
    gpd.GeoDataFrame
        Queried data.

    Examples
    --------
        query = 'SELECT * FROM c'
        comos_config = {
            'host': HHH,
            'master_key' : KKK,
            'database_id': DB,
            'container_id': CCC
        }
        dates = [{'from': '2024-10-14', 'to': '2024-10-31'}]
        df = cosmos_db_to_geodataframe(query, cosmos_config, dates)
        print(type(df))
        >>> GeoDataFrame
    """
    host = cosmos_config["host"]
    master_key = cosmos_config["master_key"]
    database_id = cosmos_config["database_id"]
    container_id = cosmos_config["container_id"]

    enable_cross_partition_query = kwargs.get("enable_cross_partition_query", False)

    client = cosmos_client.CosmosClient(
        host,
        {"masterKey": master_key},
        user_agent="CosmosDBPythonQuickstart",
        user_agent_overwrite=True,
    )

    # setup database for this sample
    db = client.get_database_client(database_id)
    container = db.get_container_client(container_id)

    if not dates:
        result = query_container(
            container=container,
            query=query,
            cross_partitions=enable_cross_partition_query,
        )
    else:
        # don't use get because we want to throw an
        # exception if date_col is not in kwargs
        date_col = kwargs["date_col"]
        result = query_between_dates(
            container=container,
            dates=dates,
            query=query,
            date_col=date_col,
            cross_partition=enable_cross_partition_query,
        )

    geo_res = cosmos_geom_to_geojson(result)
    geo_res = gpd.read_file(json.dumps(geo_res))

    if dates and not geo_res.empty:
        dates = parse_dates(dates, False, False)
        dt_col = kwargs["date_col"].split(".")[-1] + "time"
        geo_res[dt_col] = pd.to_datetime(geo_res[dt_col], format="ISO8601", utc=True)
        mask = False
        for date in dates:
            mask = mask | (
                (geo_res[dt_col] >= date["from"]) & (geo_res[dt_col] <= date["to"])
            )
        geo_res = geo_res[mask].copy()

    return geo_res
