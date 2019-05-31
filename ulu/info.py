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
def get_product_kwargs(product,date_index=None,region_index=None):
    meta=load.meta(product)
    run_cfig=meta['run']
    product_cfig=meta['product']
    model_cfig=meta['model']
    input_cfig=meta['input']
    bands_cfig=meta['bands']
    name=product_cfig['name']
    product_id=product_cfig.get(
        'product_id',
        h.product_id(product_cfig['name'],product_cfig.get('owner')))
    product_title=h.product_title(product_cfig['name'],product_cfig.get('title'))
    res,size,pad=h.resolution_size_padding(meta=meta)
    product_bands=[ b['name'] for b in bands_cfig ]
    regions=h.extract_list(run_cfig['regions'],region_index)
    return {
            'product_id': product_id,
            'title': product_title,
            'description': product_cfig.get('description',name),
            'read': product_cfig.get('read'),
            'start_datetime': run_cfig['start_date'],
            'end_datetime': run_cfig['end_date'],
            'resolution': res,
            'notes': { 
                'product': name,
                'regions': regions,
                'start_datetime': run_cfig['start_date'],
                'end_datetime': run_cfig['end_date'],
                'resolution': res,
                'size': size,
                'pad': pad,
                'water_mask': 'water_mask' in product_bands,
                'cloud_mask': 'cloud_mask' in product_bands,
                'input_products': input_cfig['products'],
                'input_bands': input_cfig['bands'],
                'window': run_cfig['window'],
                'model_filename': model_cfig.get('filename')
            }
        }



def get_delete_product_kwargs(product,cascade):
    """ product.delete """
    cfig=load.meta(product,'product')
    product_id=cfig.get(
        'product_id',
        h.product_id(cfig['name'],cfig.get('owner')))
    return {
            'product_id': product_id,
            'cascade': cascade
        }


def get_bands_kwargs_list(product):
    """ product.add_bands """
    meta=load.meta(product)
    product_cfig=meta['product']
    band_cfigs=meta['bands']
    band_defaults=meta.get('band_defaults',{})
    product_id=h.product_id(product_cfig['name'],product_cfig.get('owner'))
    bands_kwargs_list=[]
    default_resolution=band_defaults.get(
        'resolution',
        h.strip_to_int(product_cfig['resolution'],'m') 
    )
    for i,band in enumerate(band_cfigs):
        b=deepcopy(band_defaults)
        b['product_id']=product_id
        b['srcband']=i+1
        b['resolution']=band.pop('resolution',default_resolution)
        b['read']=b.get('read',product_cfig.get('read'))
        b.update(band)
        bands_kwargs_list.append(b)
    return bands_kwargs_list


def get_model_kwargs(product):
    """ model.upload/delete """
    model_cfig=load.meta(product,'model')
    model_cfig['key']=h.model_key(model_cfig['key'],model_cfig.get('dls_root'))
    return model_cfig


def get_scenes_kwargs(product,region,limit):
    """ setup.scenes """
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
    """ predict.predict """
    meta=load.meta(product)
    run_cfig=meta['run']
    product_cfig=meta['product']
    model_cfig=meta['model']
    input_cfig=meta['input']
    bands_cfig=meta['bands']
    product_id=product_cfig.get(
        'product_id',
        h.product_id(product_cfig['name'],product_cfig.get('owner')))
    product_bands=[ b['name'] for b in bands_cfig ]
    res,_,pad=h.resolution_size_padding(meta=meta)
    tiles_path=get_tiles_path(product,region,limit)
    scenes_path=get_scenes_path(tiles_path,product)
    scene_set=os.path.basename(scenes_path)
    return {
            'product': product_cfig['name'],
            'product_id': product_id,
            'bands': [ b['name'] for b in bands_cfig ],
            'model_filename': model_cfig.get('filename'),
            'model_key': model_cfig.get('key'),
            'window': run_cfig['window'],
            'water_mask': WATER_MASK_BAND in product_bands,
            'cloud_mask': CLOUD_MASK_BAND in product_bands,
            'input_products': input_cfig['products'],
            'input_bands': input_cfig['bands'],
            'resolution': res,
            'pad': pad,
            'nb_scenes': run_cfig['nb_scenes'],
            'start_date': run_cfig['start_date'],
            'end_date': run_cfig['end_date'],
            'scene_set': scene_set
        }












