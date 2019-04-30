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

#
# GET META/KWARGS
#
def get_config(product,date_index=None,region_index=None):
    meta=load.meta(product)
    res,size,pad=h.resolution_size_padding(meta=meta)
    run_cfig=meta['run']
    product_cfig=meta['product']
    input_cfig=meta['input']
    dates=h.extract_list(run_cfig['dates'],date_index)
    regions=h.extract_list(run_cfig['regions'],region_index)
    product_bands=product_cfig['bands']
    return {
            'product': product_cfig['name'],
            'model': h.model_name(**run_cfig['model']),
            'model_filename': run_cfig['model'].get('filename'),
            'model_key': run_cfig['model'].get('key'),
            'window': run_cfig['window'],
            'water_mask': 'water_mask' in product_bands,
            'cloud_mask': 'cloud_mask' in product_bands,
            'input_products': input_cfig['products'],
            'input_bands': input_cfig['bands'],
            'resampler': input_cfig['resampler'],
            'resolution': res,
            'size': size,
            'pad': pad,
            'regions': regions,
            'dates': dates
        }


def scene_level_config_list(
        tile_key,
        input_products,
        start,
        end,
        region_name=None,
        data=None):
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
    data_list=[]
    for scene_id in scenes.each.properties.id:
        scene_data=deepcopy(data)
        scene_data['scene_id']=scene_id
        scene_data['date']=h.extract_date(scene_id)
        data_list.append(scene_data)
    return data_list



def config_list(product,date_index=None,region_index=None,limit=None):
    timer=Timer()
    cfig=get_config(product,date_index,region_index)
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
                        cfig )
            out=mproc.map_with_threadpool(
                _tile_config_list,
                tile_keys,
                max_processes=MAX_THREADPOOL_PROCESSES)
            cfig_list.append(h.flatten_list(out))
    print("- {} [{}]".format(timer.stop(),timer.duration()))
    return h.flatten_list(cfig_list)