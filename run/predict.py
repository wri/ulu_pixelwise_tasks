from __future__ import print_function
import math
import json
import copy
from pprint import pprint
import numpy as np
import dl_jobs.catalog as catalog
import utils.load as load
import utils.dlabs as dlabs
from utils.generator import get_padding

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
    if index is None:
        return lst
    else:
        return [lst[index]]


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
        print(region_name)
        tiles=dlabs.get_tiles(product,region_name)
        for d in dates:  
            print(d)
            start=d['start']
            end=d['end']
            for tile in tiles[:2]:
                scenes,ctx=dlabs.get_scenes(
                    meta['run']['products'],
                    tile,
                    start,
                    end)
                print(tile.key,len(scenes))
                for scene in scenes:
                    print(scene.properties.id)
                    args=copy.deepcopy(args_base)
                    args['tile']=tile
                    args['scene']=scene
                    args['region_name']=region_name
                    args_list.append(args)
    return args_list



#
# TASKS
#
