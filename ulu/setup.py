from __future__ import print_function
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from descarteslabs.scenes import DLTile
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
RESAMPLER='bilinear'
CLOUD_SCORE_BANDS="blue green red"
DATE_PROPERTIES=[
    "properties.date.year",
    "properties.date.month",
    "properties.date.day" ]


#
# HELPERS
#
def stack_data(scene_ids,tile_key,input_bands,raster_info=True):
    if isinstance(scene_ids,str):
        scene_ids=[scene_ids]
    tile=DLTile.from_key(tile_key)
    sc=dlabs.grouped_scene_collection(scene_ids)
    return sc.stack(
        bands=input_bands,
        ctx=tile,
        flatten=DATE_PROPERTIES,
        mask_nodata=True,
        mask_alpha=None,
        bands_axis=-1,
        resampler=RESAMPLER,
        raster_info=raster_info)


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
        resampler=RESAMPLER,
        raster_info=True )
    stack_clouds=masks.stack_cloud_mask(stack)
    scores=stack_clouds.mean(axis=(1,2))
    grouped_scenes=scenes.groupby(*DATE_PROPERTIES)
    if return_stack:
        return list(scores), grouped_scenes, stack, rinfo
    else:
        return list(scores), grouped_scenes


def get_scenes_data(
        input_products,
        tile_key,
        start_date,
        end_date,
        nb_scenes=None,
        return_stack=False):
    data=cloud_scores_grouped_scenes(
        input_products,
        tile_key,
        start_date,
        end_date,
        return_stack )
    if return_stack:
        scores, grouped_scenes, stack, rinfo=data
    else:
        scores, grouped_scenes=data
    dates,scene_ids_list=dates_scene_ids(grouped_scenes)
    scores,dates,scene_ids_list=h.sortby(scores,dates,scene_ids_list)
    if nb_scenes:
        cloud_scores=scores[:nb_scenes]
        dates=dates[:nb_scenes]
        scene_ids=scene_ids_list[:nb_scenes]
    if return_stack:
        return scores, dates, scene_ids_list, stack, rinfo
    else:
        return scores, dates, scene_ids_list


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
    scores,dates,scene_ids_list=get_scenes_data(
        input_products,
        tile_key,
        start_date,
        end_date,
        nb_scenes)
    meta['cloud_scores']=scores
    meta['dates']=dates
    meta['scene_ids']=scene_ids_list
    meta['tile_key']=tile_key
    meta['nb_scenes']=nb_scenes
    meta['start_date']=start_date
    meta['end_date']=end_date
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




