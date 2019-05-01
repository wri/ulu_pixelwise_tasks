from __future__ import print_function
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import numpy as np
import descarteslabs as dl
from descarteslabs.client.services.catalog import Catalog
from dl_jobs.decorators import as_json, expand_args, attempt
import utils.helpers as h
import utils.masks as masks
from utils.generator import ImageSampleGenerator
from config import WINDOW,WINDOW_PADDING,RESAMPLER
import ulu.model
#
#   CONSTANTS
#
DTYPE='float32'



#
# PREDICTION
#
def prediction(
        arr,
        model_key=None,
        model_filename=None,
        window=WINDOW,
        pad=WINDOW_PADDING,
        prep_image=True):
    generator=ImageSampleGenerator(
        arr,
        pad=pad,
        look_window=window,
        prep_image=prep_image)
    size=arr.shape[1]-2*h.get_padding(pad,window)
    try:
        model=ulu.model.load(
            key=model_key,
            filename=model_filename)
        preds=model.predict_generator(
            generator, 
            steps=generator.steps, 
            verbose=0,
            use_multiprocessing=False,
            max_queue_size=1,
            workers=1 )
    except:
        """ TMP EXCEPTION: SHOULD LOAD FROM DLS """
        preds=np.random.random(size*size*3)
    return preds.reshape((size,size,3),order='F')


def category_prediction(preds,mask):
    """ changing behavior to drop padding """
    lulc=preds.argmax(axis=-1)
    lulc[mask]=255
    return lulc



#
# IMAGE
#
def product_image(
        product,
        scene_id,
        tile_key,
        bands,
        input_bands,
        window,
        model_key,
        model_filename,
        pad=WINDOW_PADDING,
        resampler=RESAMPLER,
        cloud_mask=False,
        water_mask=True ):
    scene,_=dl.scenes.Scene.from_id(scene_id)
    tile=dl.scenes.DLTile.from_key(tile_key)
    im,rinfo=scene.ndarray(
        bands=input_bands,
        ctx=tile,
        resampler=resampler,
        raster_info=True)
    rinfo['bands']=bands
    pad=h.get_padding(pad,window)
    blank_mask=masks.blank_mask(im,pad)
    preds=prediction(
        im.astype(DTYPE),
        model_key=model_key,
        model_filename=model_filename,
        window=window,
        pad=pad)
    lulc=category_prediction(preds,blank_mask)
    cmask,cscores=masks.cloud_score(im,window=window,pad=pad)
    cscores=h.crop(cscores,pad)
    band_images=[ lulc, preds.max(axis=-1), cscores ]
    if water_mask:
        band_images.append(masks.water_mask(im,blank_mask))
    if cloud_mask:
        band_images.append(h.crop(cmask,pad))
    return np.dstack(band_images), rinfo




#
# JOB METHODS
#
PRODUCT_IMAGE_ARGS=[
    'product',
    'scene_id',
    'tile_key',
    'bands',
    'input_bands',
    'window',
    'model_key',
    'model_filename',
    'pad',
    'resampler',
    'cloud_mask',
    'water_mask' 
]
RASTER_META_ARGS=[
    'scene_id',
    'tile_key',
    'input_bands',
    'region_name',
    'cloud_mask',
    'water_mask',
    'model_key',
    'date',
]
IMAGE_ID_ARGS=[
    'input_products',
    'product',
    'scene_id',
    'tile_key'
]
@as_json
@attempt
@expand_args
def predict(*args,**kwargs):
    """ PREDICTION METHOD """
    product_id=kwargs.pop('product_id')
    meta=h.extract_kwargs(kwargs,RASTER_META_ARGS)
    image_id_args=[kwargs[k] for k in IMAGE_ID_ARGS]
    image_id=h.image_id(*image_id_args)
    prod_im_kwargs=h.extract_kwargs(kwargs,PRODUCT_IMAGE_ARGS)
    im,rinfo=product_image(**prod_im_kwargs)
    upload_id=Catalog().upload_ndarray(
            ndarray=im,
            product_id=product_id,
            image_id=image_id,
            raster_meta=rinfo,
            extra_properties=meta,
            acquired=meta['date'] )
    out={
        'ACTION': 'predict',
        'SUCCESS': True,
        'upload_id': upload_id,
        'image_id': image_id,
        'product_id': product_id,
        'shape': im.shape
    }
    return out














