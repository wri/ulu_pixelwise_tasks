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


def region_path(region,ext='shp'):
    rparts=region.split('.')
    if rparts[-1]=='geojson':
        ext='geojson'
        region='.'.join(rparts[:-1])
    selector='{}/{}/*.{}'.format(
        REGIONS_DIR,
        region.lower(),
        ext)
    paths=glob(selector)
    if len(paths)>1:
        raise ValueError("Multiple paths found: {}".format(paths))
    elif paths:
        return paths[0]
    else:
        raise ValueError("Region ({}) does not exist".format(region))


def geodataframe(region=None,path=None,ext='shp'):
    if not path:
        path=region_path(region=region,ext=ext)
    return gpd.read_file(path)
        

def shape(region=None,path=None,ext='shp'):
    return geojson.loads(geodataframe(region,path,ext).geometry.to_json())







