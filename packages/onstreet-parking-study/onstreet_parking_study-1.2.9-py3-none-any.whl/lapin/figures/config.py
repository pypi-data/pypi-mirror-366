import numpy as np
import contextily as ctx
from lapin.figures import colors

######################
###### REMPLA ########
######################

REMPLA_UNDETERMINED_HANDLE = {
    'undtermined': ['Très court', 'Court'],
    'merged': ['Long'],
}

######################
#### NUMERIC CUTS ####
######################

LEGEND_LABEL = {
    'first': 'Inf. à {0}',
    'middle': 'Entre {0} et {1}',
    'last': 'Sup. à {0}',
}

OCC_NUM_CUTS = {
    'Inférieure à 50%':   0.50,
    'Entre 50% et 80%':   0.80,
    'Entre 80% et 90%':   0.90,
    'Supérieure à 90%':  np.inf
}

CAPA_NUM_CUTS = {
 'Inf. à 5': 5,
 'Entre 5 et 15': 15,
 'Entre 15 et 25': 25,
 'Sup. à 25': np.inf
}

PROV_NUM_CUTS = {
 'Inf. à 5%': 5,
 'Entre 5% et 10%': 10,
 'Entre 10% et 15%': 15,
 'Entre 15% et 20%': 20,
 'Sup. à 20%': np.inf
}

CAPA_NORM_NUM_CUTS = {
    'Inférieur à 20%':  0.2,
    'Entre 20% et 40%': 0.4,
    'Entre 40% et 60%': 0.6,
    'Entre 60% et 80%': 0.8,
    'Sup. à 80%':       np.inf
}

OCC_RELATIV_CUTS = {
    'Baisse importante (-100% à -50%)':    0.50,
    'Baisse légère (-50% à -10%)':     0.90,
    'Pas de changement (-10% à +10%)':  1.10,
    'Augmentation légère (+10% à +50%)':  1.50,
    'Augmentation importante (sup à +50%)':  2,
}

REMPLA_NUM_CUTS = {
    'Inf. à 30min':      0.5,
    'Entre 30min et 2H': 2,
    'Entre 2H et 5H30':  5.5,
    'Sup. à 5H30':       np.inf
}

#######################
#### LEGEND COLORS ####
#######################

#assign colors
BASIC_CAT_COLORS = {
    'Travaux': colors.LAPIN_COLORS['TRAVAUX'],
    'Aucune place': colors.LAPIN_COLORS['NO_PLACES'],
    'Non parcourue': colors.LAPIN_COLORS['HORS_ZONE'],
    'Voie réservée': colors.LAPIN_COLORS['VR'],
    'Sans donnée' : colors.LAPIN_COLORS['MISSING_GREY'],
    "N'a plus de stationnements" : '#b0f2b6',
}

RELATIV_CAT_COLORS = BASIC_CAT_COLORS
#{
#    'Sans données' : colors.LAPIN_COLORS['MISSING_GREY']
#}

OCC_LABELS = list(OCC_NUM_CUTS.keys())
OCC_COLORS = {
    OCC_LABELS[0] : '#77B77D', #colors.LAPIN_PALETTES['OCC_BLUES'](as_cmap=True)(0.40),
    OCC_LABELS[1] : '#549EB3', #colors.LAPIN_PALETTES['OCC_BLUES'](as_cmap=True)(0.60),
    OCC_LABELS[2] : '#6059A9', #colors.LAPIN_PALETTES['OCC_BLUES'](as_cmap=True)(0.80),
    OCC_LABELS[3] : '#882E72', #colors.LAPIN_PALETTES['OCC_BLUES'](as_cmap=True)(1.00),
}

OCCR_LABELS = list(OCC_RELATIV_CUTS.keys())
OCC_RELATIV_COLORS = {
    OCCR_LABELS[0] : colors.LAPIN_PALETTES['OCC_VLAG'](n_colors=5)[0],
    OCCR_LABELS[1] : colors.LAPIN_PALETTES['OCC_VLAG'](n_colors=5)[1],
    OCCR_LABELS[2] : colors.LAPIN_PALETTES['OCC_VLAG'](n_colors=5)[2],#'lightgray',#colors.LAPIN_PALETTES['OCC_VLAG'](n_colors=5)[2],
    OCCR_LABELS[3] : colors.LAPIN_PALETTES['OCC_VLAG'](n_colors=5)[3],
    OCCR_LABELS[4] : colors.LAPIN_PALETTES['OCC_VLAG'](n_colors=5)[4],
}

CAPA_LABELS = list(CAPA_NUM_CUTS.keys())
CAPA_COLORS = {
    CAPA_LABELS[0] : colors.LAPIN_PALETTES['CAPA'](as_cmap=True)(0.25),
    CAPA_LABELS[1] : colors.LAPIN_PALETTES['CAPA'](as_cmap=True)(0.50),
    CAPA_LABELS[2] : colors.LAPIN_PALETTES['CAPA'](as_cmap=True)(0.75),
    CAPA_LABELS[3] : colors.LAPIN_PALETTES['CAPA'](as_cmap=True)(1.00),
}

CAPA_NORM_LABELS = list(CAPA_NORM_NUM_CUTS.keys())
CAPA_NORM_COLORS = {
    CAPA_NORM_LABELS[0] : colors.LAPIN_PALETTES['CAPA'](as_cmap=True)(0.20),
    CAPA_NORM_LABELS[1] : colors.LAPIN_PALETTES['CAPA'](as_cmap=True)(0.40),
    CAPA_NORM_LABELS[2] : colors.LAPIN_PALETTES['CAPA'](as_cmap=True)(0.60),
    CAPA_NORM_LABELS[3] : colors.LAPIN_PALETTES['CAPA'](as_cmap=True)(0.80),
    CAPA_NORM_LABELS[4] : colors.LAPIN_PALETTES['CAPA'](as_cmap=True)(1.00),
}

REMPLA_LABELS = list(REMPLA_NUM_CUTS.keys())
REMPLA_COLORS = {
    REMPLA_LABELS[0] : colors.LAPIN_PALETTES['OCC_BLUES'](as_cmap=True)(0.30),
    REMPLA_LABELS[1] : colors.LAPIN_PALETTES['OCC_BLUES'](as_cmap=True)(0.60),
    REMPLA_LABELS[2] : colors.LAPIN_PALETTES['OCC_BLUES'](as_cmap=True)(0.80),
    REMPLA_LABELS[3] : colors.LAPIN_PALETTES['OCC_BLUES'](as_cmap=True)(1.00),
}


###############
#### TILES ####
###############

MAPBOX_API_KEY = 'pk.eyJ1IjoiYWxhdXJlbnQzNCIsImEiOiJja28xcnFocTIwb2QyMnd0ZG5oc2pvaDl4In0.iOefsxCQnpJSarh39T2aIg'

MAPBOX_DARK = {
    'url': 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}',
    'id': 'mapbox/dark-v10',
    'tile_size': 512,
    'max_zoom': 18,
    'zoom_offset': -1,
    'attribution': '',
    'accessToken': MAPBOX_API_KEY
}
MAPBOX_DARK = ctx.providers.MapBox(**MAPBOX_DARK)

MAPBOX_LIGHT = {
    'url': 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}',
    'id': 'mapbox/light-v10',
    'tile_size': 256,
    'max_zoom': 18,
    'zoom_offset': 0,
    'attribution': '',
    'accessToken': MAPBOX_API_KEY
}
MAPBOX_LIGHT = ctx.providers.MapBox(**MAPBOX_LIGHT)

ESRI_WORLD_STREET = ctx.providers.Esri.WorldStreetMap
ESRI_WORLD_STREET['attribution'] = ''

CURRENT_TILE = MAPBOX_LIGHT

ROAD_SHAPE = 'data/figs/roads_qc.geojson'
HYDRO_SHAPE = 'data/figs/hydrographie_qc.geojson'

######################
#### IMAGE OUTPUTS ###
######################

FIG_DPI = 100
MAP_DPI = 250
LEG_DPI = 100
