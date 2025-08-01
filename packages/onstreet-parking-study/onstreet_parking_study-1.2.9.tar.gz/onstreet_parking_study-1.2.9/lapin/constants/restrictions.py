import numpy as np

VEH_SIZE = 5.5

# columns
CAP_START_RES = 'deb'
CAP_END_RES = 'fin'
CAP_RES_DT_FROM = 'res_date_debut'
CAP_RES_DT_TO = 'res_date_fin'
CAP_RES_HOUR_TO = 'res_hour_to'
CAP_RES_HOUR_FROM = 'res_hour_from'
CAP_RES_DAYS = 'res_days'
CAP_RES_TYPE = 'res_type'
CAP_RESTRICTIONS = 'restrictions'
CAP_IS_RESTRICT = 'is_restrict'
CAP_DELIM_SPACE = 'longueur_marquée'
CAP_SPACE = 'longueur_non_marquée'
CAP_N_DELIM_S   = 'nb_places_marquées'
CAP_N_UNDELIM_S = 'nb_places_non_marquées'
CAP_N_VEH = 'nb_places_total'
CAP_CACHE_PATH = './cache'
CAP_MINIMAL_LENGTH = 3

# priorty
CAP_PRIORITY = [
    'Non parcourue',
    'Travaux',
    'Premier/Dernier 5m',
    'Borne fontaine',
    'Entrée Charretière',
    'Entrée Charettière',
    'Arrêt de bus',
    'Interdiction',
    'Traverse piétonne',
    'SPVM',
    'Taxi',
    'Entretien',
    'SRRR',
    'Non-définie'
]

# zone to ignore for restrictions and capacity
IGNORE_FOR_CAPACITY = [
    'Handicap',
    'Durée limitée',
    'SRRR'
]

# default computation for capacity
CAP_DAYS_HOUR_TO_COMPUTE = {
    'lun-dim': {'from':'07:30', 'to':'20:30', 'step':'1'},
}

# French week-day/week-end
FRENCH_WEEK_DAY_CAT = {
    0:'Semaine',
    1:'Semaine',
    2:'Semaine',
    3:'Semaine',
    4:'Semaine',
    5:'Fin de semaine',
    6:'Fin de semaine',
}

DEFAULT_COLS_CRUNCH = {
    CAP_N_VEH: 'sum',
}
