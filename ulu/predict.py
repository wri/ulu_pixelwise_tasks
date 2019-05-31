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
import utils.dlabs as dlabs
from utils.generator import ImageSampleGenerator
from config import WINDOW,WINDOW_PADDING,RESAMPLER
import ulu.model
from ulu.setup import get_scenes_data
import tensorflow as tf
from mproc import MPList


from pprint import pprint
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


#
# PRODUCT
#
def product_image(
        product,
        tile_key,
        scene_ids,
        im,
        rinfo,
        bands,
        input_bands,
        window,
        model_key,
        model_filename,
        pad=WINDOW_PADDING,
        cloud_mask=False,
        water_mask=True ):
    rinfo['bands']=bands
    pad=h.get_padding(pad,window)
    blank_mask=masks.blank_mask(im,pad)
    """ multiprocess """
    mp_list=MPList()
    mp_list.append(
        prediction,
        im.astype(DTYPE),
        model_key=model_key,
        model_filename=model_filename,
        window=window,
        pad=pad )
    mp_list.append(
        masks.cloud_score,
        im,
        window=window,
        pad=pad )
    preds,(cmask,cscores)=mp_list.run()
    """" end-multiprocess """
    lulc=category_prediction(preds,blank_mask)
    cscores=h.crop(cscores,pad)
    band_images=[ preds.max(axis=-1), lulc, cscores ]
    if water_mask:
        band_images.append(masks.water_mask(im,blank_mask))
    if cloud_mask:
        band_images.append(h.crop(cmask,pad))
    return np.dstack(band_images), rinfo



#
# JOB METHODS
#
@as_json
# @attempt
@expand_args
def predict(
        product,
        product_id,
        region,
        input_products,
        tile_key,
        nb_scenes,
        start_date,
        end_date,
        bands,
        input_bands,
        window,
        model_key,
        model_filename,
        pad,
        resolution,
        scene_set,
        scene_ids=None,
        cloud_scores=None,
        dates=None,
        cloud_mask=False,
        water_mask=True,
        ERROR=None,
        ARGS=None,
        KWARGS=None ):
    meta={
            'model': model_filename,
            'tile_key': tile_key,
            'region_name': region,
            'resolution': resolution,
            'scene_set': scene_set,
            'cloud_mask': str(cloud_mask),
            'water_mask': str(water_mask)
        }
    if ERROR:
        return {
            'WARNING': 'error in scene',
            'SCENE_ERROR': ERROR,
            'SCENE_ARGS': ARGS,
            'SCENE_KWARGS': KWARGS,
            'meta': meta
        }
    else:
        if not scene_ids:
            cloud_scores, dates, scene_ids=get_scenes_data(
                input_products,
                tile_key,
                start_date,
                end_date,
                nb_scenes)
        stack, rinfo=dlabs.stack(
            scene_ids,
            tile_key,
            input_bands)
        for i in range(len(scene_ids)):
            meta['date']=dates[i]
            meta['cloud_score']=cloud_scores[i]
            meta['scene_ids']=str(scene_ids[i])
            im,rinfo=product_image(
                product=product,
                tile_key=tile_key,
                scene_ids=scene_ids[i],
                im=stack[i],
                rinfo=rinfo,
                bands=bands,
                input_bands=input_bands,
                window=window,
                model_key=model_key,
                model_filename=model_filename,
                pad=pad,
                cloud_mask=cloud_mask,
                water_mask=water_mask )
            image_id=h.image_id(
                input_products,
                product,
                scene_ids[i],
                tile_key)
            return _upload_scene(product_id,image_id,im,rinfo,meta)


def _upload_scene(product_id,image_id,im,rinfo,meta):
    upload_id=Catalog().upload_ndarray(
            ndarray=im,
            product_id=product_id,
            image_id=image_id,
            raster_meta=rinfo,
            extra_properties=meta,
            acquired=meta['date'] )
    hist=np.unique(im[:,:,1],return_counts=True)
    cats=hist[0]
    counts=hist[1]
    if isinstance(cats,np.ma.core.MaskedArray):
        cats=cats.data
    cats=[ int(c) for c  in cats ]
    counts=[ int(c) for c  in counts ]
    return {
        'ACTION': 'predict',
        'SUCCESS': True,
        'upload_id': upload_id,
        'image_id': image_id,
        'product_id': product_id,
        'shape': im.shape,
        'hist': {
            'categories': list(cats),
            'counts': list(counts)
        }
    }

