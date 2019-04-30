import warnings
import yaml
import geojson
from glob import glob
import geopandas as gpd
from keras.models import load_model
import keras.backend as K
from config import REGIONS_DIR,PRODUCTS_DIR,MODELS_DIR
warnings.filterwarnings("ignore", category=DeprecationWarning)



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
        

def models_list(ext='hd5'):
    return glob('{}/*.{}'.format(MODELS_DIR,ext))


def model(key=None,filename=None,path=None,nb_cats=3):
    """ TODO: LOAD VIA KEY """
    if not path:
        path='{}/{}'.format(MODELS_DIR,filename)
    return load_model(
        path, 
        custom_objects={'loss':'categorical_crossentropy'})




