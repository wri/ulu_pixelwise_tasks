import math
import json
from pprint import pprint
import numpy as np
import dl_jobs.catalog as catalog


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
# CONFIG
#
DEFAULT_SIZE=4



#
# TASKS
#
def task(
        dl_id,
        tile=None,
        tile_id=None,
        network=None,
        read_local=False,
        write_local=True,
        make_watermask=True,
        store_cloudmask=False,
        store_watermask=False,
        bands=['blue','green','red','nir','swir1','swir2','alpha'],
        resampler='bilinear',
        #cutline=shape['geometry'], #cut or no?
        processing_level=None,
        window=17,
        data_root='/data/phase_iv/',
        zfill=4
    ):
    print('delete/add_product')
    catalog.delete_product()
    out=catalog.add_product()
    bands=catalog.add_bands(out['data']['id'])
    if read_local:
        im,meta=catalog.get_image()
    else:
        im,meta=catalog.dl_get_image()
    meta['bands']=bands
    print("TEST OUT:")
    print('--',im.shape)
    im=catalog.preprocess(im)
    preds=catalog.predictions(im)
    if write_local:
        catalog.local_write(preds,'test_im.tif',meta)
    else:
        catalog.dl_write(preds,'test_im.tif',meta)
    out={
        'done':True,
        'dl_id': dl_id,
        'tile': tile,
        'tile_id': tile_id,
        'shape': im.shape
    }
    print('COMPLETE',out)
    return json.dumps(out)


