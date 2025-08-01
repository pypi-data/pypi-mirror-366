""" This module provide function to read and preprocess some of the montreal's
open data portal datasets """
import urllib.request
import geopandas as gpd

from lapin import constants


def read_mtl_open_data(url: str, encoding: str = 'utf-8') -> gpd.GeoDataFrame:
    """_summary_

    Parameters
    ----------
    url : _type_
        _description_
    encoding : str, optional
        _description_, by default 'utf-8'

    Returns
    -------
    _type_
        _description_
    """
    req = urllib.request.urlopen(url)
    lines = req.readlines()
    if not encoding:
        encoding = req.headers.get_content_charset()
    lines = [line.decode(encoding) for line in lines]
    data = gpd.read_file(''.join(lines))

    return data


def clean_geobase_mtl(
    data: gpd.GeoDataFrame,
    **kwargs
) -> gpd.GeoDataFrame:
    """_summary_

    Parameters
    ----------
    data : pd.DataFrame
        _description_

    Returns
    -------
    pd.DataFrame
        _description_
    """
    data = data.copy()

    data = data.rename(columns={
        'ID_TRC': constants.SEGMENT,
        'SENS_CIR': constants.TRAFFIC_DIR,
        'NOM_VOIE': constants.HR_ROAD_NAME
    })

    return data


def clean_geobase_dbl_mtl(
    data: gpd.GeoDataFrame,
    **kwargs
) -> gpd.GeoDataFrame:
    """_summary_

    Parameters
    ----------
    data : pd.DataFrame
        _description_

    Returns
    -------
    pd.DataFrame
        _description_
    """
    data = data.copy()
    data = data.rename(columns={
        'ID_TRC': constants.SEGMENT,
        'SENS_CIR': constants.TRAFFIC_DIR,
        'NOM_VOIE': constants.ROAD_NAME
    })
    data[constants.SIDE_OF_STREET] = data[constants.SEG_DB_SIDE].map(
        constants.SEG_DB_SIDE_OF_STREET_MAP
    )

    return data


ROADS_CONNECTION_MTL = {
    'type': 'mtl_opendata',
    'url': 'https://donnees.montreal.ca/dataset/984f7a68-ab34-4092-9204-4bdfcca767c5/resource/9d3d60d8-4e7f-493e-8d6a-dcd040319d8d/download/geobase.json',
    'post_processing': False,
    'func': clean_geobase_mtl
}

ROADS_CONNECTION = {
    'type': 'curbsnapp',
    'config': {
        'projects_list': [],
        'geobase_type': 'simple'}
}

ROADS_DB_CONNECTION_MTL = {
    'type': 'mtl_opendata',
    'url': 'https://donnees.montreal.ca/dataset/88493b16-220f-4709-b57b-1ea57c5ba405/resource/16f7fa0a-9ce6-4b29-a7fc-00842c593927/download/gbdouble.json',
    'post_processing': True,
    'func': clean_geobase_dbl_mtl
}

ROADS_DB_CONNECTION = {
    'type': 'curbsnapp',
    'config': {
        'projects_list': [],
        'geobase_type': 'double'},
    'post_processing': True,
    'func': clean_geobase_dbl_mtl
}
