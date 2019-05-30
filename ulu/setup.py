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
import dl_jobs.helpers as dh
#
# CONSTANTS
#
CLOUD_SCORE_BANDS="blue green red"
DATE_PROPERTIES=[
    "properties.date.year",
    "properties.date.month",
    "properties.date.day" ]


#
# HELPERS
#
def cloud_scores_grouped_scenes(
        input_products,
        tile_key,
        start_date,
        end_date,
        return_stack=False):
    scenes,ctx=dlabs.get_scenes(
        input_products,
        tile_key,
        start_date,
        end_date )
    stack,rinfo=scenes.stack(
        CLOUD_SCORE_BANDS, 
        ctx,
        flatten=DATE_PROPERTIES,
        mask_nodata=True,
        mask_alpha=None,
        bands_axis=-1,
        raster_info=True,
        resampler='bilinear' )
    stack_clouds=masks.stack_cloud_mask(stack)
    scores=stack_clouds.mean(axis=(1,2))
    grouped_scenes=scenes.groupby(*DATE_PROPERTIES)
    if return_stack:
        return stack, rinfo, scores, grouped_scenes
    else:
        return list(scores), grouped_scenes


def dates_scene_ids(grouped_scenes):
    date_scene_ids=[_date_scene_ids(d,s) for d,s in grouped_scenes]
    dates,scene_ids_list=list(zip(*date_scene_ids))
    return dates,scene_ids_list


#
# JOBS
#
@as_json
@attempt
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
    meta['tile_key']=tile_key
    scores, grouped_scenes=cloud_scores_grouped_scenes(
        input_products,
        tile_key,
        start_date,
        end_date )
    dates,scene_ids_list=dates_scene_ids(grouped_scenes)
    scores,dates,scene_ids_list=h.sortby(scores,dates,scene_ids_list)
    meta['cloud_scores']=scores[:nb_scenes]
    meta['dates']=dates[:nb_scenes]
    meta['scene_ids']=scene_ids_list[:nb_scenes]
    return meta




#
# INTERNAL
#
def _date_scene_ids(date_tuple,grouped_scenes):
    return ( 
        "-".join(map(str,date_tuple)),
        list(grouped_scenes.each.properties.id) )


def _img_date_scene_ids(img,date_tuple,grouped_scenes):
    return (img,)+_scene_ids(date_tuple,grouped_scenes)




