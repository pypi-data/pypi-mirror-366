""" Module for configuration variables"""
import logging
from importlib_resources import files

logger = logging.getLogger(__name__)

# TODO: shoot in conf file
DISCRETISATION_CONNECTION = {
    'type': 'fiona',
    'filename': files('lapin').joinpath('../data/limites/regions_analyse.geojson')
    }

PLAQUE_CONNECTION = {
    'type': 'xls',
    'filename': ''
    }

PLAQUE_IDX_CONNECTION = {
    'type': 'xls',
    'filename': ''
    }

TYPE_PLAQUE_CONNECTION = {
    'type': 'xls',
    'filename': ''
    }

GEOREF_CP_CONNECTION = {
    'type': 'fiona',
    'filename': ''
    }

DELIM_CONNECTION = {
    'type': 'fiona',
    'filename': ''
    }

VIS_DELIM_CONNECTION = {
    'type': 'fiona',
    'filename': ''
    }

PROV_CONF = {
    "act_prov": '',
    "cp_base_filename": '',
    "cp_folder_path": '',
    "cp_regions_bounds": '',
    "cp_regions_bounds_names": '',
    "plates_periods": '',
    "cp_conf": '',
}
