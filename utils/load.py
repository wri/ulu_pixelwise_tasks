import yaml
import geojson
from glob import glob
import geopandas as gpd
import tensorflow as tf
from tensorflow.keras.models import load_model
import tensorflow.keras.backend as K
from config import STUDY_AREAS_DIR,PRODUCTS_DIR,MODELS_DIR



def meta(product,*keys):
    """ get product meta data
        - product: str 
        - *keys: order sequence of dictionary keys
    """
    meta=yaml.safe_load(open('{}/{}.yaml'.format(PRODUCTS_DIR,product)))
    for key in keys:
        meta=meta[key]
    return meta



def shape(study_area=None,path=None,ext='shp'):
    if not path:
        selector='{}/{}/*.{}'.format(
            STUDY_AREAS_DIR,
            study_area.lower(),
            ext)
        path=glob(selector)[0]
    return geojson.loads(gpd.read_file(path).geometry.to_json())


def models_list(ext='hd5'):
    return glob('{}/*.{}'.format(MODELS_DIR,ext))


def model(path=None,filename=None,nb_cats=3):
    if not path:
        path='{}/{}'.format(MODELS_DIR,filename)
    return load_model(
        path, 
        custom_objects={'loss':make_loss_function_wcc([1]*nb_cats)})


def make_loss_function_wcc(weights):
    """ make loss function: weighted categorical crossentropy
        Args:
            * weights<ktensor|nparray|list>: crossentropy weights
        Returns:
            * weighted categorical crossentropy function
    """
    if isinstance(weights,list) or isinstance(weights,np.ndarray):
        weights=K.variable(weights)

    def loss(target,output,from_logits=False):
        if not from_logits:
            output /= tf.reduce_sum(output,
                                    len(output.get_shape()) - 1,
                                    True)
            _epsilon = tf.convert_to_tensor(K.epsilon(), dtype=output.dtype.base_dtype)
            output = tf.clip_by_value(output, _epsilon, 1. - _epsilon)
            weighted_losses = target * tf.log(output) * weights
            return - tf.reduce_sum(weighted_losses,len(output.get_shape()) - 1)
        else:
            raise ValueError('WeightedCategoricalCrossentropy: not valid with logits')

    return loss




