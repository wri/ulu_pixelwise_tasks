from __future__ import print_function
import math
import json
from pprint import pprint
import numpy as np
import dl_jobs.catalog as catalog
import helpers as h


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
GPUS=None

#
# TASKS
#
def task(scene,bands,resampler,tile_key):
    arr=scene.ndarray(
        bands=bands,
        ctx=ctx,
        resampler=resampler)
    predictions=ulu.predictions(arr)
    cloud_mask, cloud_scores=ulu.cloud_scores(arr, window, tile_pad=tile_pad)
    lulc=ulu.lulc(predictions,np.invert(arr[-1].astype(bool)))
    if make_watermask:
        water_mask = util_imagery.calc_water_mask(im[:-1], bands_first=True)
        water_mask[blank_mask] = 255
    else:
        water_mask = None
    product_image=ulu.product_image(lulc,predictions,cloud_mask,water_mask)
    image_id=ulu.image_id(products,product_name,scene,tile)
    if write_local:
        h.write(product_im,image_id,meta)
    else:
        catalog.dl_write(product_im,image_id,meta)
    out={
        'TODO':True
    }
    print('COMPLETE',out)
    return json.dumps(out)


