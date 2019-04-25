from __future__ import print_function
import re
import numpy as np
import utils.helpers as h
import utils.masks as masks
from utils.generator import WINDOW_PADDING, ImageSampleGenerator, get_padding
#
#   CONSTANTS
#
DTYPE='float32'
RESAMPLER='bilinear'


#
#   HELPERS
#
def image_id(products,product_name,scene,tile_key=None):
    s_id=scene.properties.id
    name=next(re.sub('^{}'.format(p),product_name,s_id) for p in products if p in s_id)
    if tile_key:
        name='{}:{}'.format(name,tile_key)
    return name


#
#  PREDICTION
#
def predict(model,arr,window,pad,prep_image=True):
    generator=ImageSampleGenerator(
        arr,
        pad=pad,
        look_window=window,
        prep_image=prep_image)
    preds=model.predict_generator(
        generator, 
        steps=generator.steps, 
        verbose=0,
        use_multiprocessing=False,
        max_queue_size=1,
        workers=1,)
    size=arr.shape[1]-2*get_padding(pad,window)
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
        scene,
        ctx,
        input_bands,
        model,
        window,
        pad=WINDOW_PADDING,
        resampler=RESAMPLER,
        include_cloud_mask=False,
        include_water_mask=True):
    pad=get_padding(pad,window)
    im=scene.ndarray(
        bands=input_bands,
        ctx=ctx,
        resampler=resampler)
    blank_mask=masks.blank_mask(im,pad)
    preds=predict(model,im.astype(DTYPE),window,pad)
    lulc=category_prediction(preds,blank_mask)
    cloud_mask,cloud_scores=masks.cloud_score(im,window=window,pad=pad)
    cloud_scores=h.crop(cloud_scores,pad)
    band_images=[ lulc, preds.max(axis=-1), cloud_scores ]
    if include_water_mask:
        band_images.append(masks.water_mask(im,blank_mask))
    if include_cloud_mask:
        band_images.append(h.crop(cloud_mask,pad))
    return np.dstack(band_images)



def product_meta(
        products,
        product_name,
        tile_key,
        scene,
        input_bands,
        model_name,
        model_file,
        window,
        include_cloud_mask=False,
        include_water_mask=True):
    name=image_id(products,product_name,scene,tile_key)
    """ add all meta vars """
    pass





