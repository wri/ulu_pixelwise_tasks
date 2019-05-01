from __future__ import print_function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import yaml
import geojson
from glob import glob
import geopandas as gpd
from config import REGIONS_DIR,PRODUCTS_DIR

def meta(product,*keys):
    """ get product meta data
        - product: str 
        - *keys: order sequence of dictionary keys
    """
    meta=yaml.safe_load(open('{}/{}.yaml'.format(PRODUCTS_DIR,product)))
    for key in keys:
        meta=meta[key]
    return meta


def shape(region=None,path=None,ext='shp'):
    if not path:
        selector='{}/{}/*.{}'.format(
            REGIONS_DIR,
            region.lower(),
            ext)
        path=glob(selector)[0]
    return geojson.loads(gpd.read_file(path).geometry.to_json())
        





