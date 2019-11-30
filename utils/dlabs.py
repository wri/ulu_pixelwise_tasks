from __future__ import print_function
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import json
from pprint import pprint
import descarteslabs as dl
from descarteslabs.scenes import Scene, SceneCollection, DLTile
import utils.helpers as h
import utils.load as load
import dl_jobs.helpers as dh
#
# CONSTANTS
#
RESAMPLER='bilinear'
DATE='date'
DATE_PROPERTIES=[
    "properties.date.year",
    "properties.date.month",
    "properties.date.day" ]


#
# HELPERS
#
def get_scenes(products,aoi,start_date,end_date):
    if dh.is_str(aoi):
        aoi=DLTile.from_key(aoi)
    return dl.scenes.search(
        products=products,
        aoi=aoi,
        start_datetime=start_date,
        end_datetime=end_date )


def scenes_list(scene_ids):
    return [s for (s,_) in (Scene.from_id(sid) for sid in scene_ids)]


def scene_collection(scene_ids,groupby=None):
    if isinstance(scene_ids[0],list):
        scene_ids=h.flatten_list(scene_ids)
    sc=SceneCollection(scenes_list(scene_ids))
    if groupby==DATE:
        groupby=DATE_PROPERTIES
    if groupby:
        sc=sc.groupby(*groupby)
    return sc


def stack(
        scene_ids,
        tile,
        input_bands,
        flatten=DATE_PROPERTIES,
        raster_info=True,
        rinfo_list=False):
    if dh.is_str(scene_ids):
        scene_ids=[scene_ids]
    if dh.is_str(tile):
        tile=DLTile.from_key(tile)
    sc=scene_collection(scene_ids)
    stack_data=sc.stack(
        bands=input_bands,
        ctx=tile,
        flatten=flatten,
        mask_nodata=True,
        mask_alpha=None,
        bands_axis=-1,
        resampler=RESAMPLER,
        raster_info=raster_info)
    if (not raster_info) or rinfo_list:
        return stack_data
    else:
        stk,rinfo=stack_data
        return stk, rinfo[0]


def update_tile_key_padding(tile_key,padding=0):
    parts=tile_key.split(":")
    return ":".join([parts[0],str(padding)]+parts[2:])


def raster_info(aoi,bands):
    if dh.is_str(aoi):
        aoi=DLTile.from_key(aoi)
    meta=_coordinate_info(aoi).copy()
    meta['bands']=bands
    return meta




#
# MAIN
#
"""
* MULTI FEATURE TILES FOR HANDLED IN NOTEBOOK FOR NOW
"""
def get_tile_keys(
        product=None,
        region=None,
        limit=None,
        path=None,
        return_info=False ):
    meta=load.meta(product)
    res,size,pad=h.resolution_size_padding(meta=meta)
    info={}
    info['region']=region
    info['path']=path
    info['limit']=limit
    if path and os.path.isfile(path):
        info['existing_file']=True
        info['saved']=None
        tile_keys=h.read_pickle(path)
    else:
        info['existing_file']=False
        shape=load.shape(region)
        tiles=DLTile.from_shape(
                shape=shape, 
                resolution=res, 
                tilesize=size, 
                pad=pad )
        tile_keys=[t.key for t in tiles]
        if limit:
            tile_keys=tile_keys[:limit]
        if path:
            info['saved']=True
            h.save_pickle(tile_keys,path)
        else:
            info['saved']=False
    info['tile_count']=len(tile_keys)
    if return_info:
        return tile_keys, info
    else:
        return tile_keys



#
# INTERNAL
#
def _coordinate_info(aoi):
    sz=aoi.tilesize + (2 * aoi.pad)
    meta={
        'coordinateSystem': {
            'proj4': aoi.proj4,
            'wkt': aoi.wkt
        },
        'driverLongName': 'In Memory Raster',
        'driverShortName': 'MEM',
        'geoTransform': aoi.geotrans,
        'metadata': {'': {'Corder': 'RPCL', 'id': '*'}},
        'size': [sz, sz],
        'files': []
    }
    return meta



