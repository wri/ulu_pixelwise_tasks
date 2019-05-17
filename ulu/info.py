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
#
# CONSTANTS
#
MAX_THREADPOOL_PROCESSES=32
TILES_EXIST='ERROR[ulu.save_tiles]: tile_set ({}) exists. use force=True to overwrite'


#
# GET META/KWARGS
#
def get_tiles_path(product,region,limit):
    meta=load.meta(product)
    run_cfig=meta['run']
    name=run_cfig.get('tile_set')   
    if name:
        path='{}/{}'.format(directory,name)
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


def get_config(product,date_index=None,region_index=None):
    meta=load.meta(product)
    res,size,pad=h.resolution_size_padding(meta=meta)
    run_cfig=meta['run']
    product_cfig=meta['product']
    model_cfig=meta['model']
    input_cfig=meta['input']
    bands_cfig=get_bands_config(product)
    product_bands=[ b['name'] for b in bands_cfig ]
    dates=h.extract_list(run_cfig['dates'],date_index)
    regions=h.extract_list(run_cfig['regions'],region_index)
    product_id=h.product_id(product_cfig['name'],product_cfig.get('owner'))
    product_title=h.product_title(product_cfig['name'],product_cfig.get('title'))
    return {
            'product': product_cfig['name'],
            'product_id': product_id,
            'title': product_title,
            'description': product_cfig.get('description','name'),
            'model': h.model_name(**model_cfig),
            'model_filename': model_cfig.get('filename'),
            'model_key': model_cfig.get('key'),
            'window': run_cfig['window'],
            'water_mask': 'water_mask' in product_bands,
            'cloud_mask': 'cloud_mask' in product_bands,
            'input_products': input_cfig['products'],
            'input_bands': input_cfig['bands'],
            'bands': bands_cfig,
            'resolution': res,
            'size': size,
            'pad': pad,
            'regions': regions,
            'dates': dates,
            'config_list_name': run_cfig.get('config_list_name')
        }


def scene_level_config_list(
        tile_key,
        input_products,
        start,
        end,
        region_name=None,
        data=None,
        nb_scenes=False ):
    if data: 
        data=deepcopy(data)
    else:
        data={}
    data['region_name']=region_name
    data['tile_key']=tile_key
    scenes,_=dlabs.get_scenes(
        input_products,
        tile_key,
        start,
        end )
    if nb_scenes:
        data['nb_scenes']=int(nb_scenes)
        data['scene_ids']=list(scenes.each.properties.id)
        return [data]
    else:
        data_list=[]
        for scene_id in scenes.each.properties.id:
            scene_data=deepcopy(data)
            scene_data['scene_id']=scene_id
            scene_data['date']=h.extract_date(scene_id)
            data_list.append(scene_data)
        return data_list


def config_list(
        product,
        date_index=None,
        region_index=None,
        limit=None,
        config_list_name=None,
        nb_scenes=False ):
    cfig=get_config(product,date_index,region_index)
    if not config_list_name:
        config_list_name=cfig.get('config_list_name',False)
    path=h.config_list_path(
        config_list_name,
        product=product,
        size=cfig['size'],
        window=cfig['window'] )
    if path and os.path.isfile(path):
        cfig_list=h.read_pickle(path)
    else:
        timer=Timer()
        regions=cfig.pop('regions')
        dates=cfig.pop('dates')
        print("\ncreating kwarg_list:")
        print("- {}".format(timer.start()))
        cfig_list=[]
        for region_name in regions:
            tile_keys=dlabs.get_tile_keys(product,region_name)
            if limit:
                tile_keys=tile_keys[:limit]
            for date in dates:
                def _tile_config_list(tile_key):
                    return scene_level_config_list(
                            tile_key,
                            cfig['input_products'],
                            date['start'],
                            date['end'],
                            region_name,
                            cfig,
                            nb_scenes )
                out=mproc.map_with_threadpool(
                    _tile_config_list,
                    tile_keys,
                    max_processes=MAX_THREADPOOL_PROCESSES)
                cfig_list.append(h.flatten_list(out))
        print("- {} [{}]".format(timer.stop(),timer.duration()))
        cfig_list=h.flatten_list(cfig_list)
        if path: 
            h.save_pickle(cfig_list,path)
    return cfig_list


