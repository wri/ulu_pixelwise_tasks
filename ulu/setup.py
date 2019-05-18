from __future__ import print_function
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from dl_jobs.decorators import as_json, expand_args, attempt
import utils.helpers as h
import utils.dlabs as dlabs
import utils.load as load
import utils.masks as masks
from config import TILES_DIR
from dl_jobs.utils import Timer
#
# CONSTANTS
#
CLOUD_SCORE_BANDS="blue green red"


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
def save_scenes(
        input_products,
        tile_key,
        nb_scenes,
        start_date,
        end_date,
        **meta):
    scenes,ctx=dlabs.get_scenes(
        input_products,
        tile_key,
        start_date,
        end_date )
    meta['tile_key']=tile_key
    stack=scenes.stack(
        CLOUD_SCORE_BANDS, 
        ctx, 
        mask_nodata=True,
        mask_alpha=None,
        bands_axis=-1,
        raster_info=False,
        resampler='bilinear')    
    stack_clouds=masks.stack_cloud_mask(stack)
    scores=stack_clouds.mean(axis=(1,2))
    scene_ids=list(scenes.each.properties.id)
    scene_scores=[
        {'scene_id': sid,'date': h.extract_date(sid),'cloud_score': cs } for 
        sid,cs in 
        zip(scene_ids,scores)]
    sorted(scene_scores,key=lambda d: d['cloud_score'])
    scene_scores=scene_scores[:nb_scenes]
    scene_scores=[ h.copy_update(meta,d) for d in scene_scores ]
    return scene_scores




def copy_update(data,update,value=None):
    data=deepcopy(data)
    if update:
        if isinstance(update,dict):
            data.update(update)
        else: 
            data[update]=value
    return data


