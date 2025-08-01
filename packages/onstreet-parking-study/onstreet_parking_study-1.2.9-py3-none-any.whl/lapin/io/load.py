"""_summary_ """

import os
import itertools
import pandas as pd
import geopandas as gpd

from lapin.io.sqlalchemy_utils import get_engine
from lapin.io.azure_cosmos import cosmos_db_to_geodataframe
from lapin.configs.mtl_opendata import read_mtl_open_data
from lapin.constants.geom import DEFAULT_CRS
from lapin.tools.curbsnapp import get_project_geobases, get_geobase


def data_from_conf(
    data_config: dict,
) -> pd.DataFrame | gpd.GeoDataFrame | tuple[gpd.GeoDataFrame | pd.DataFrame, object]:
    """Read a configuration file and return the DataFrame associated.

    Parameters
    ----------
    data_config: dict
        Dictionnary containing the configuration

    Returns
    -------
    pd.DataFrame
        Data in memory

    Raises
    ------
    ValueError
        If type is geodata, the config should contain key CRS
    NotImplementedError
        If type is not in (sql, fiona, xls, azure_cosmos)
    """
    others = None
    if data_config["type"] == "sql":
        con = get_engine(**data_config)
        data = pd.read_sql(con=con, sql=data_config.get("sql", ""))

    elif data_config["type"] == "fiona":
        data = gpd.read_file(**data_config)
        if data.crs is None:
            raise ValueError(
                f'Missing crs for {data_config["filename"]},' + "cannot proceed further"
            )
        data = data.to_crs(DEFAULT_CRS)

    elif data_config["type"] == "mtl_opendata":
        url = data_config.get("url", None)
        encoding = data_config.get("encoding", "utf-8")
        if not url:
            raise ValueError("Missing url in config.")
        data = read_mtl_open_data(url, encoding)

    elif data_config["type"] == "xls":
        data = pd.read_excel(data_config["filename"])

    elif data_config["type"] == "curbsnapp":
        data, others = get_project_geobases(**data_config["config"])

    elif data_config["type"] == "curbsnapp_geobase":
        data, others = get_geobase(**data_config["config"])

    elif data_config["type"] == "azure_cosmos":
        data = cosmos_db_to_geodataframe(
            query=data_config["query"],
            cosmos_config=data_config["cosmos_conf"],
            dates=data_config.get("dates", []),
            date_col=data_config.get("date_col", ""),
            enable_cross_partition_query=data_config.get(
                "enable_cross_partition_query", False
            ),
        )

    else:
        raise NotImplementedError("Type should be in sql, fiona or xls")

    if data_config.get("post_processing", False):
        data = data_config["func"](data, data_config=data_config.get("config", {}))

    if others:
        return data, others

    return data


def saaq_data(
    base_filename: str,
    folder_path: str,
    regions_bounds_path: str,
    regions_bounds_names: str,
    periods: dict,
    geocode_conf: dict,
) -> pd.DataFrame:
    """Transform SAAQ request about plates to trips

    Parameters
    ----------
    base_filename : str
        Structure of the name for all SAAQ dataset
    folder_path : str
        Where to read the SAAQ data
    regions_bounds_path : str
        Where to read regions of analysis for provenance
    regions_bounds_names : str
        Region columns names
    periods : dict
        Periods to analyse (SAAQ).
    geocode_conf : dict
        Configuration of the geospatial data for RTA UDL

    Returns
    -------
    pd.DataFrame
        The "Trips" generated with the SAAQ datasets
    """
    basefilename = base_filename
    regions = gpd.read_file(regions_bounds_path).to_crs("epsg:32188")
    regions_list = regions[regions_bounds_names].to_list()
    cp_gis = data_from_conf(geocode_conf)

    data = []
    for r, p, w in itertools.product(regions_list, *periods.values()):
        data_tmp = pd.read_excel(
            os.path.join(folder_path, basefilename.format(r, p, w))
        )
        data_tmp.columns = [
            "rtaudl",
            "champ2",
            "code_muni",
            "muni",
            "code_region",
            "nb_plaque",
        ]
        data_tmp = data_tmp[["rtaudl", "nb_plaque"]]
        data_tmp["region"] = r
        data_tmp["period"] = p
        data_tmp["week_day"] = w
        centroid = (
            regions.loc[regions[regions_bounds_names] == r]
            .centroid.to_crs("epsg:4326")
            .values[0]
        )
        data_tmp["dest_lat"] = centroid.y
        data_tmp["dest_lng"] = centroid.x
        data_tmp = data_tmp[~data_tmp.rtaudl.isna()]
        data_tmp.rtaudl = data_tmp.rtaudl.str.upper()
        data.append(data_tmp)

    data = pd.concat(data)
    data = data.join(
        cp_gis.set_index("postalcode")[["geometry"]], on="rtaudl", how="inner"
    )
    data["ori_lat"] = data.geometry.apply(lambda x: x.centroid.y)
    data["ori_lng"] = data.geometry.apply(lambda x: x.centroid.x)
    data = data.drop(columns="geometry")

    # repeat count to have single veh trips
    data = data.reset_index(drop=True)
    data = data.loc[data.index.repeat(data.nb_plaque)]
    data = data.reset_index(drop=True)
    data = data.drop(columns="nb_plaque")

    return data
