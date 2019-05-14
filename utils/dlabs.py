from __future__ import print_function
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import json
from pprint import pprint
import descarteslabs as dl
import utils.helpers as h
import utils.load as load
#
# PUBLIC
#
def get_tiles(
        product=None,
        region=None,
        auto_save=True,
        return_info=False):
    meta=load.meta(product)
    res,size,pad=h.resolution_size_padding(meta=meta)
    path=h.tiles_path(region,res,size,pad)
    info={}
    info['region']=region
    info['path']=path
    if os.path.isfile(path):
        info['existing_file']=True
        info['saved']=None
        tiles=h.read_pickle(path)
    else:
        info['existing_file']=False
        shape=load.shape(region)
        tiles=dl.scenes.DLTile.from_shape(
                shape=shape, 
                resolution=res, 
                tilesize=size, 
                pad=pad )
        if auto_save:
            info['saved']=True
            h.save_pickle(tiles,path)
        else:
            info['saved']=False
            info['path']=None
    info['nb_tiles']=len(tiles)
    if return_info:
        return tiles, info
    else:
        return tiles


def get_tile_keys(
        product=None,
        region=None,
        auto_save=True,
        return_info=False):
    meta=load.meta(product)
    res,size,pad=h.resolution_size_padding(meta=meta)
    path=h.tile_keys_path(region,res,size,pad)
    info={}
    info['region']=region
    info['path']=path
    if os.path.isfile(path):
        info['existing_file']=True
        info['saved']=None
        tile_keys=h.read_pickle(path)
    else:
        info['existing_file']=False
        shape=load.shape(region)
        tiles=dl.scenes.DLTile.from_shape(
                shape=shape, 
                resolution=res, 
                tilesize=size, 
                pad=pad )
        tile_keys=[t.key for t in tiles]
        if auto_save:
            info['saved']=True
            h.save_pickle(tile_keys,path)
        else:
            info['saved']=False
            info['path']=None
    info['nb_tiles']=len(tile_keys)
    if return_info:
        return tile_keys, info
    else:
        return tile_keys


def get_scenes(products,aoi,start,end):
    if h.is_str(aoi):
        aoi=dl.scenes.DLTile.from_key(aoi)
    return dl.scenes.search(
        products=products,
        aoi=aoi,
        start_datetime=start,
        end_datetime=end )


