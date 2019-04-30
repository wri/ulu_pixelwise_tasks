from __future__ import print_function
import os
import numpy as np
import descarteslabs as dl
from dl_jobs.decorators import as_json, expand_args
import utils.helpers as h
import utils.load as load
import utils.masks as masks
from utils.generator import ImageSampleGenerator
from config import WINDOW,WINDOW_PADDING,RESAMPLER
#
#   CONSTANTS
#
DTYPE='float32'



#
#  PREDICTION
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
    model=load.model(
        key=model_key,
        filename=model_filename)
    preds=model.predict_generator(
        generator, 
        steps=generator.steps, 
        verbose=0,
        use_multiprocessing=False,
        max_queue_size=1,
        workers=1,)
    size=arr.shape[1]-2*h.get_padding(pad,window)
    return preds.reshape((size,size,3),order='F')


def category_prediction(preds,mask):
    """ changing behavior to drop padding """
    lulc=preds.argmax(axis=-1)
    lulc[mask]=255
    return lulc



#
#   PRODUCT
#
def product_image(
        scene_id,
        tile_key,
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
    im=scene.ndarray(
        bands=input_bands,
        ctx=tile,
        resampler=resampler)
    pad=h.get_padding(pad,window)
    blank_mask=masks.blank_mask(im,pad)
    preds=prediction(
        im.astype(DTYPE),
        model_filename=model_filename,
        window=window,
        pad=pad)
    lulc=category_prediction(preds,blank_mask)
    cloud_mask,cloud_scores=masks.cloud_score(im,window=window,pad=pad)
    cloud_scores=h.crop(cloud_scores,pad)
    band_images=[ lulc, preds.max(axis=-1), cloud_scores ]
    if water_mask:
        band_images.append(masks.water_mask(im,blank_mask))
    if cloud_mask:
        band_images.append(h.crop(cloud_mask,pad))
    return np.dstack(band_images)




#
# JOB METHODS
#
PRODUCT_IMAGE_ARGS=[
    'scene_id',
    'tile_key',
    'input_bands',
    'window',
    'model_key',
    'model_filename',
    'pad',
    'resampler',
    'cloud_mask',
    'water_mask' 
]
PRODUCT_IMAGE_META=[
    'product',
    'scene_id',
    'tile_key',
    'input_bands',
    'model',
    'window',
    'resolution',
    'size',
    'pad',
    'cloud_mask',
    'water_mask',
    'region_name',
    'date',
]
@as_json
@expand_args
def predict(**kwargs):
    """ PREDICTION METHOD """
    meta=h.extract_kwargs(kwargs,PRODUCT_IMAGE_META)
    kwargs=h.extract_kwargs(kwargs,PRODUCT_IMAGE_ARGS)
    im=product_image(**kwargs)
    # upload_product_image(im,meta)
    kwargs['tmp_im_stats']={
        'shape': im.shape
    }
    return kwargs














