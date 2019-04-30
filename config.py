import os


#
# DIRECTORIES
#
HOME=os.path.expanduser('~')
PROJECT_DIR=os.path.dirname(os.path.realpath(__file__))
PRODUCTS_DIR='{}/products'.format(PROJECT_DIR)
DATA_DIR='{}/data'.format(PROJECT_DIR)
REGIONS_DIR='{}/regions'.format(DATA_DIR)
MODELS_DIR='{}/models'.format(DATA_DIR)


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
