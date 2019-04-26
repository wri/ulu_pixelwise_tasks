from __future__ import print_function
import math
import json
import copy
from pprint import pprint
import numpy as np
import mproc
from dl_jobs.job import DLJob
import dl_jobs.catalog as catalog
import utils.helpers as h
import utils.load as load
import utils.dlabs as dlabs
from utils.generator import get_padding

MAX_THREADPOOL_PROCESSES=32

#
# CONSTANTS
#
TEST_WARN_TMP="TEST-MODE: executing sing task [{}]"
CONFIG_METHODS=[
    'test',
    'tasks'
]

#
# DL FUNCTION ARGS
#
DATA=None
MODULES=[
    'run',
    'dl_jobs'
]
REQUIREMENTS=[
    'descarteslabs[complete]>=0.17.3',
    'numpy==1.16.2',
    'rasterio==1.0.22',
    'affine==2.2.2'
]
GPUS=1


#
# HELPERS
#
def extract_list(lst,index):
    if (index is None) or (index is 'None'):
        return lst
    else:
        return [lst[int(index)]]


def get_tile_args_list(tile,region_name,products,start,end,args=None):
    args_list=[]
    scenes,ctx=dlabs.get_scenes(
        products,
        tile,
        start,
        end )
    if not args: args={}
    for scene in scenes:
        args['products']=products
        args['tile_key']=tile.key
        args['scene']=scene
        args['region_name']=region_name
        args_list.append(args)
    return args_list



def prediction_args_list(product,date_index=None,region_index=None):
    meta=load.meta(product)
    dates=extract_list(meta['run']['dates'],date_index)
    regions=extract_list(meta['run']['regions'],region_index)
    args_base={
        'input_bands': meta['inputs']['bands'],
        'product_name': meta['product']['name'],
        'window': meta['run']['window'],
        'model_filename': meta['run']['model'],
        'pad': get_padding(meta['run']['pad'],meta['run']['window'])
    }
    args_list=[]
    for region_name in regions:
        tiles=dlabs.get_tiles(product,region_name)
        for d in dates:  
            def _arg_list(tile):
                return get_tile_args_list(
                        tile,
                        region_name,
                        meta['run']['products'],
                        d['start'],
                        d['end'],
                        copy.deepcopy(args_base) )
            out=mproc.map_with_threadpool(
                _arg_list,
                tiles,
                max_processes=MAX_THREADPOOL_PROCESSES)
            args_list.append(h.flatten_list(out))
    return h.flatten_list(args_list)



#
# TASKS
#
def test(*args,**kwargs):
    product=args[0]
    if len(args)>1:
        task_index=args[1]
    else:
        task_index=0
    date_index=kwargs.get('date',None)
    region_index=kwargs.get('region',None)
    print(TEST_WARN_TMP.format(task_index))
    print(product,task_index,date_index,region_index)
    kwargs.pop('args_list',False)
    args_list=prediction_args_list(
        product,
        date_index=date_index,
        region_index=region_index)
    print('==',len(args_list))
    args=args_list[task_index]
    pprint(args)
    job=DLJob(
        module_name='utils.ulu',
        method_name='product_meta',
        args_list=args_list,
        modules=MODULES,
        requirements=REQUIREMENTS,
        data=DATA,
        gpus=GPUS,
        **kwargs )
    return job




def tasks(product,date_index=None,region_index=None):
    product=h.first(product)
    args_list=prediction_args_list(
        product,
        date_index=date_index,
        region_index=region_index)
    # save_product_image.map(args_list)


def predict(*args):
    print('\n'*5)
    print('-'*100)
    print(args)
    # return {'keys':args[0].keys(),'len':len(args)}
    return json.dumps({'keys':type(args),'len':len(args)})


