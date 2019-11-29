import os


#
# DIRECTORIES
#
HOME=os.path.expanduser('~')
PROJECT_DIR=os.path.dirname(os.path.realpath(__file__))
PRODUCTS_DIR='{}/products'.format(PROJECT_DIR)
DATA_DIR='{}/data'.format(PROJECT_DIR)
TILES_DIR='{}/tiles'.format(DATA_DIR)
SCENES_DIR='{}/scenes'.format(DATA_DIR)
RESULTS_DIR='{}/results'.format(DATA_DIR)
REGIONS_DIR='{}/regions'.format(DATA_DIR)
MODELS_DIR='{}/models'.format(DATA_DIR)
STORAGE_DIR='/cache'
DLS_ROOT='models/dev'
CONFG_LIST_DIR='{}/config_lists'.format(DATA_DIR)


#
# DL/PRODUCTS
#
USER='6d27def1bb7fb0138933a4ee2e33cce9f5af999a'



#
# OTHER
#
WINDOW=17
WINDOW_PADDING='window'
RESAMPLER='bilinear'
CONFIRM_DELETE="ULU.product.delete/remove: pass 'confirm=True' to delete product/band/model"
WATER_MASK_BAND='water_mask'
CLOUD_MASK_BAND='cloud_mask'


#
# DATA
#
VALUE_CATEGORIES={
    0: 'Open Space',
    1: 'Non-Residential',
    2: 'Residential Atomistic',
    3: 'Residential Informal Subdivision',
    4: 'Residential Formal Subdivision',
    5: 'Residential Housing Project',
    6: 'No Data',
}
NB_CATS=len(VALUE_CATEGORIES)


""" COLORS:
0    Open Space    #b2df8a  (178, 223, 138)
1    Non-Residential    #fb9a99 (251,154,153)
4    Residential    #1f78b4  (31, 120, 180)
6    Roads    #e31a1c (227, 26, 28)
"""



