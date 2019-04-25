from __future__ import print_function
import os
import warnings
import json
from pprint import pprint
import descarteslabs as dl
import config as c
import utils.helpers as h
import utils.load as load
warnings.filterwarnings("ignore", category=DeprecationWarning)

#
# CONFIG
#
ALIGN_PIXELS=False


#
# PUBLIC
#
def get_tiles(product=None,region=None,auto_save=True,return_info=False):
    product=h.first(product)
    meta=load.meta(product,'product')
    res,size,pad=meta['resolution'],meta['size'],meta['pad']
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
            info['path']=None
            info['saved']=False
    info['nb_tiles']=len(tiles)
    if return_info:
        return tiles, info
    else:
        return tiles



def get_scenes(products,tile,start,end):
    aoi=dl.scenes.AOI(
        geometry=tile,
        resolution=tile.resolution,
        crs=tile.crs,
        bounds=tile.bounds,
        bounds_crs=tile.bounds_crs,        
        align_pixels=ALIGN_PIXELS )
    return dl.scenes.search(
        products=products,
        aoi=aoi,
        start_datetime=start,
        end_datetime=end )


