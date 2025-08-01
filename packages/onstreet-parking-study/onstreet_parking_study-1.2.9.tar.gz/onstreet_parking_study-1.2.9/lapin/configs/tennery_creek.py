""" This module provide function to post_process tennery-creek
    data after reading it raw from conf.
"""

from lapin.configs.database import STAGING_DATABASE
from lapin.constants.lpr_data import DATE_KWARGS


# Vehicule detection
LPR_CONNECTION = {
    "engine_conf": STAGING_DATABASE,
    "schema": "tannery",
    "table": "vehicle_detection_enhanced",
    "dates": [],
    "date_col": "datetime",
    "tdf_columns_config": {
        "plate": "plaque",
        "latitude": "lat",
        "longitude": "lng",
        "datetime": "datetime",
        "user_id": "veh_id",
        "side_of_car": "side_of_car",
        "date_kwargs": DATE_KWARGS,
    },
}

# Vehicule trajectory
VEH_CONNECTION = {
    "engine_conf": STAGING_DATABASE,
    "schema": "tannery",
    "table": "vehicle_trajectory_enhanced",
    "dates": [],
    "date_col": "datetime",
    "tdf_columns_config": {
        "latitude": "lat",
        "longitude": "lng",
        "datetime": "datetime",
        "user_id": "veh_id",
        "date_kwargs": DATE_KWARGS,
    },
}
