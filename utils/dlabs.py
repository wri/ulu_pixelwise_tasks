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
        tiles=dl.scenes.DLTile.from_shape(
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


def get_scenes(products,aoi,start_date,end_date):
    if h.is_str(aoi):
        aoi=dl.scenes.DLTile.from_key(aoi)
    return dl.scenes.search(
        products=products,
        aoi=aoi,
        start_datetime=start_date,
        end_datetime=end_date )


