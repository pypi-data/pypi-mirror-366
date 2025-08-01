from lapin.configs.database import STAGING_DATABASE

ROAD_NET_CONNECTION = {
    "engine_conf": STAGING_DATABASE,
    "schema": "curbsnapp",
    "table": "geobase",
    "columns_config": {
        "id_": "id_trc",
        "road_name": "nom_voie",
        "traffic_dir": "sens_cir",
    },
}

ROAD_DBL_CONNECTION = {
    "engine_conf": STAGING_DATABASE,
    "schema": "curbsnapp",
    "table": "geobase_double",
    "columns_config": {
        "id_": "id_trc",
        "road_name": "nom_voie",
        "traffic_dir": "sens_cir",
        "side_of_street": "cote",
    },
}
