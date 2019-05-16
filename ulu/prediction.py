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
import tensorflow as tf

from pprint import pprint
#
#   CONSTANTS
#
DTYPE='float32'
RESAMPLER='bilinear'



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
    return preds.reshape((size,size,3),order='F')


def category_prediction(preds,mask):
    """ changing behavior to drop padding """
    lulc=preds.argmax(axis=-1)
    lulc[mask]=255
    return lulc



def image_data(scene_id,tile_key,input_bands):
    scene,_=dl.scenes.Scene.from_id(scene_id)
    tile=dl.scenes.DLTile.from_key(tile_key)
    return scene.ndarray(
        bands=input_bands,
        ctx=tile,
        resampler=RESAMPLER,
        raster_info=True)


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
        cloud_mask=False,
        water_mask=True,
        im=None,
        rinfo=None ):
    if im is None:
        im,rinfo=image_data(scene_id,tile_key,input_bands)
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
    band_images=[ preds.max(axis=-1), lulc, cscores ]
    if water_mask:
        band_images.append(masks.water_mask(im,blank_mask))
    if cloud_mask:
        band_images.append(h.crop(cmask,pad))
    return np.dstack(band_images), rinfo


def best_scenes(scene_ids,tile_key,input_bands,nb_scenes):
    image_data_list=[ (image_data(s,tile_key,input_bands),s) for s in scene_ids ]
    image_data_list=[ 
        ( masks.image_cloud_score(im),im,d,s ) for 
        ((im,d),s) in 
        image_data_list ]
    image_data_list=sorted(image_data_list, key=lambda x: x[0])
    return image_data_list[:nb_scenes]




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
    'cloud_mask',
    'water_mask' 
]
RASTER_META_ARGS=[
    'scene_id',
    'tile_key',
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
# @attempt
@expand_args
def predict(*args,**kwargs):
    """ PREDICTION METHOD """
    product_id=kwargs.pop('product_id')
    meta=h.extract_kwargs(kwargs,RASTER_META_ARGS)
    meta['cloud_mask']=str(meta['cloud_mask'])
    meta['water_mask']=str(meta['water_mask'])
    nb_scenes=kwargs.pop('nb_scenes',False)
    prod_im_kwargs=h.extract_kwargs(
        kwargs,
        PRODUCT_IMAGE_ARGS )
    if nb_scenes:
        scene_list=best_scenes(
            kwargs['scene_ids'],
            kwargs['tile_key'],
            kwargs['input_bands'],
            nb_scenes)
        out_list=[]
        for cs,im,rinfo,scene_id in scene_list:
            if isinstance(cs,np.ma.core.MaskedArray) or isinstance(cs,np.ndarray):
                if not cs.shape:
                    cs=cs.item()
                else:
                    raise ValueError('ULU.predict: invalid cloud_score. {}'.format(cs))
            m=meta.copy()
            m['cloud_score']=cs
            m['scene_id']=scene_id
            m['date']=h.extract_date(scene_id)
            im,rinfo=product_image(im=im,rinfo=rinfo,**prod_im_kwargs)
            image_id=h.image_id(
                    prods=kwargs['input_products'],
                    pname=kwargs['product'],
                    sid=scene_id,
                    tkey=kwargs['tile_key'] )
            out_list.append(_upload_scene(product_id,image_id,im,rinfo,m))
        return out_list
    else:
        image_id_args=[kwargs[k] for k in IMAGE_ID_ARGS]
        image_id=h.image_id(*image_id_args)
        im,rinfo=product_image(**prod_im_kwargs)
        return _upload_scene(product_id,image_id,im,rinfo,meta)


def _upload_scene(product_id,image_id,im,rinfo,meta):
    upload_id=Catalog().upload_ndarray(
            ndarray=im,
            product_id=product_id,
            image_id=image_id,
            raster_meta=rinfo,
            extra_properties=meta,
            acquired=meta['date'] )
    return {
        'ACTION': 'predict',
        'SUCCESS': True,
        'upload_id': upload_id,
        'image_id': image_id,
        'product_id': product_id,
        'shape': im.shape
    }

