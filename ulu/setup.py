from __future__ import print_function
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from dl_jobs.decorators import as_json, expand_args, attempt
import utils.helpers as h
import utils.dlabs as dlabs
import utils.load as load
from config import TILES_DIR
#
# CONSTANTS
#



#
# GET META/KWARGS
#


#
# JOBS
#
@as_json
# @attempt
@expand_args
def save_tiles(path,product,region,limit=None):
    tile_keys,meta=dlabs.get_tile_keys(
        path=path,
        product=product,
        region=region,
        limit=limit,
        return_info=True)
    meta['action']='save_tiles'
    return meta



@as_json
# @attempt
@expand_args
def save_scenes(input_products,tile_key,nb_scenes,start_date,end_date,**meta):
    scenes,ctx=dlabs.get_scenes(
        input_products,
        tile_key,
        start_date,
        end_date )
    meta.update({
        'input_products': input_products,
        'tile_key': tile_key,
        'start_date': start_date,
        'end_date': end_date,
        'nb_scenes': nb_scenes,
        'scene_count': len(scenes)
    })
    return meta







