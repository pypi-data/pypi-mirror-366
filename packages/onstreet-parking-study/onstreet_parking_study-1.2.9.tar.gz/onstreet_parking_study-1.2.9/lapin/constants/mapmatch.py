import os

VALHALLA_DFLT_FOLDER = os.path.dirname(os.path.realpath(__file__))
VALHALLA_DFLT_FOLDER = os.path.join(
    VALHALLA_DFLT_FOLDER,
    '..',
    '..',
    'data/network/valhalla/'
)
VALHALLA_DFLT_FOLDER = os.path.abspath(VALHALLA_DFLT_FOLDER)
