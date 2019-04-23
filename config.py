import os 
import yaml
#
# DIRECTORIES
#
HOME=os.path.expanduser('~')
PROJECT_DIR=os.path.dirname(os.path.realpath(__file__))
DATA_DIR=f'{PROJECT_DIR}/data'





#
# DL/PRODUCTS
#
USER='6d27def1bb7fb0138933a4ee2e33cce9f5af999a'
PRODUCTS='products'
def product_meta(product,*keys):
    """ get product meta data
        - product: str 
        - *keys: order sequence of dictionary keys
    """
    meta=yaml.safe_load(open(f'{PRODUCTS}/{product}.yaml'))
    for key in keys:
        meta=meta[key]
    return meta