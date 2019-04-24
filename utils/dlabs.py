from __future__ import print_function
import json
from pprint import pprint
import descarteslabs as dl
import config as c
import utils.helpers as h
import utils.load as load
#
# CONFIG
#
ALIGN_PIXELS=False


#
# PUBLIC
#
def get_tiles(product,study_area):
    product=h.first(product)
    meta=load.meta(product,'product')
    shape=load.shape(study_area)
    tiles=dl.scenes.DLTile.from_shape(
            shape=shape, 
            resolution=meta['resolution'], 
            tilesize=meta['size'], 
            pad=meta['pad'] )
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


