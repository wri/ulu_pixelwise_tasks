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