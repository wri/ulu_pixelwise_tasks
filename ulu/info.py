from __future__ import print_function
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from copy import deepcopy
import mproc
from dl_jobs.utils import Timer
import utils.helpers as h
import utils.load as load
import utils.dlabs as dlabs
from config import TILES_DIR, SCENES_DIR, RESULTS_DIR
from config import WATER_MASK_BAND, CLOUD_MASK_BAND
#
# GET PATHS
#
def get_tiles_path(product,region,limit):
    meta=load.meta(product)
    run_cfig=meta['run']
    name=run_cfig.get('tile_set')   
    if name:
        path='{}/{}'.format(TILES_DIR,name)
    else:
        res,size,pad=h.resolution_size_padding(meta=meta)
        version=run_cfig.get('version')
        path=h.tiles_path( 
            region,
            res,
            size,
            pad,
            version,
            limit )
    return path


def get_scenes_path(tiles_path,product):
    run_cfig=load.meta(product,'run')
    name=run_cfig.get('scene_set')   
    if name:
        path='{}/{}'.format(SCENES_DIR,name)
    else:
        nb_scenes=run_cfig['nb_scenes']
        start_date=run_cfig['start_date']
        end_date=run_cfig['end_date']
        path=h.scenes_path(
            tiles_path,
            nb_scenes,
            start_date,
            end_date)
    return path


def get_prediction_path(scenes_path,product):
    run_cfig=load.meta(product,'run')
    name=run_cfig.get('results')   
    if name:
        path='{}/{}'.format(RESULTS_DIR,name)
        add_timestamp=False
    else:
        path=scenes_path
        add_timestamp=True
    return path, add_timestamp


#
# GET ARGS/KWARGS
#
def get_scenes_kwargs(product,region,limit):
    meta=load.meta(product)
    input_cfig=meta['input']
    run_cfig=meta['run']
    return {
        'input_products': input_cfig['products'],
        'nb_scenes': run_cfig['nb_scenes'],
        'start_date': run_cfig['start_date'],
        'end_date': run_cfig['end_date'],
        'region': region }


def get_predict_kwargs(product,region,limit):
    meta=load.meta(product)
    run_cfig=meta['run']
    product_cfig=meta['product']
    model_cfig=meta['model']
    input_cfig=meta['input']
    bands_cfig=meta['bands']
    product_id=h.product_id(product_cfig['name'],product_cfig.get('owner'))
    product_title=h.product_title(product_cfig['name'],product_cfig.get('title'))
    product_bands=[ b['name'] for b in bands_cfig ]
    res,size,pad=h.resolution_size_padding(meta=meta)
    tiles_path=get_tiles_path(product,region,limit)
    scenes_path=get_scenes_path(tiles_path,product)
    tile_set=os.path.basename(tiles_path)
    scene_set=os.path.basename(scenes_path)
    return {
            'product': product_cfig['name'],
            'product_id': product_id,
            'title': product_title,
            'description': product_cfig.get('description','name'),
            'model': h.model_name(**model_cfig),
            'model_filename': model_cfig.get('filename'),
            'model_key': model_cfig.get('key'),
            'window': run_cfig['window'],
            'water_mask': WATER_MASK_BAND in product_bands,
            'cloud_mask': CLOUD_MASK_BAND in product_bands,
            'input_products': input_cfig['products'],
            'input_bands': input_cfig['bands'],
            'resolution': res,
            'size': size,
            'pad': pad,
            'tile_set': tile_set,
            'scene_set': scene_set
        }















#***********************************************************
#
# TO BE REFACTORED
#
#***********************************************************


def get_model_config(product):
    model_cfig=load.meta(product,'model')
    model_cfig['key']=h.model_key(model_cfig['key'],model_cfig.get('dls_root'))    
    return model_cfig
    

def get_bands_config(product):
    meta=load.meta(product)
    product_cfig=meta['product']
    band_cfigs=meta['bands']
    band_defaults=meta.get('band_defaults',{})
    product_id=h.product_id(product_cfig['name'],product_cfig.get('owner'))
    cfig_list=[]
    default_resolution=band_defaults.get(
        'resolution',
        h.strip_to_int(product_cfig['resolution'],'m') 
    )
    for i,band in enumerate(band_cfigs):
        b=deepcopy(band_defaults)
        b['product_id']=product_id
        b['srcband']=i+1
        b['resolution']=band.pop('resolution',default_resolution)
        b.update(band)
        cfig_list.append(b)
    return cfig_list






