from __future__ import print_function
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import numpy as np
import descarteslabs as dl
from descarteslabs.catalog import Image, Product, OverviewResampler
from descarteslabs.scenes import DLTile
from dl_jobs.decorators import as_json, expand_args, attempt
import utils.helpers as h
import utils.masks as masks
import utils.dlabs as dlabs
from utils.generator import ImageSampleGenerator
from config import WINDOW, WINDOW_PADDING, RESAMPLER
from config import VALUE_CATEGORIES, NB_CATS
import ulu.model
from ulu.scenes import get_scenes_data
import tensorflow as tf
from mproc import MPList
#
#   CONSTANTS
#
DTYPE='float32'
MULTI_PROCESS=True
OVERVIEWS=[2,4]
OVERVIEW_RESAMPLER=OverviewResampler.MODE


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
    return preds.reshape((size,size,preds.shape[-1]),order='F')


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
        input_bands,
        window,
        model_key,
        model_filename,
        pad=WINDOW_PADDING,
        cloud_mask=False,
        water_mask=True ):
    pad=h.get_padding(pad,window)
    blank_mask=masks.blank_mask(im,pad)
    if MULTI_PROCESS:
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
    else:
        preds=prediction(
            im.astype(DTYPE),
            model_key=model_key,
            model_filename=model_filename,
            window=window,
            pad=pad )
        (cmask,cscores)=masks.cloud_score(
            im,
            window=window,
            pad=pad )
    lulc=category_prediction(preds,blank_mask)
    cscores=h.crop(cscores,pad)
    band_images=[ lulc, preds.max(axis=-1), cscores ]
    if water_mask:
        band_images.append(masks.water_mask(im,blank_mask))
    if cloud_mask:
        band_images.append(h.crop(cmask,pad))
    return np.stack(band_images), lulc



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
        mode_product_id=None,
        mode_bands=None,
        ERROR=None,
        ARGS=None,
        KWARGS=None ):
    meta={
            'model': model_filename,
            'region_name': region,
            'scene_set': scene_set
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
        if not isinstance(start_date,list):
            start_date=[start_date]
            end_date=[end_date]
        outs=[]
        for start,end in zip(start_date,end_date):
            if not scene_ids:
                cloud_scores, dates, scene_ids=get_scenes_data(
                    input_products,
                    tile_key,
                    start,
                    end,
                    nb_scenes)
            stack, rinfo=dlabs.stack(
                scene_ids,
                tile_key,
                input_bands)
            scene_count=len(scene_ids)
            out=[]
            lulcs=[]
            lulc_tile_key=dlabs.update_tile_key_padding(tile_key)
            rinfo=dlabs.raster_info(lulc_tile_key,bands)
            meta['tile_key']=lulc_tile_key
            for i in range(scene_count):
                im, lulc=product_image(
                    product=product,
                    tile_key=tile_key,
                    scene_ids=scene_ids[i],
                    im=stack[i],
                    input_bands=input_bands,
                    window=window,
                    model_key=model_key,
                    model_filename=model_filename,
                    pad=pad,
                    cloud_mask=cloud_mask,
                    water_mask=water_mask )
                lulcs.append(lulc)
                image_id=h.image_id(
                    input_products,
                    product,
                    scene_ids[i],
                    lulc_tile_key)
                meta['cloud_score']=cloud_scores[i]
                meta['scene_ids']=str(scene_ids[i])
                out.append(
                    _upload_scene(
                        product_id,
                        image_id,
                        dates[i],
                        im,
                        rinfo,
                        meta))
            if mode_product_id:
                dates=h.sorted_dates(dates)
                mode_date=h.mid_date(dates[0],dates[-1])
                image_id=h.mode_image_id(
                    mode_product_id,
                    mode_date,
                    lulc_tile_key)
                mode,counts=h.mode(np.stack(lulcs))
                mode,counts=mode[0],counts[0]
                mode_im=np.stack([mode,counts/scene_count,counts])
                meta.pop('cloud_score')
                meta['date']=mode_date
                meta['dates']=', '.join(dates)
                meta['tile_score']=mode_im[0].mean()
                meta['scene_count']=scene_count
                rinfo['bands']=mode_bands
                out.append(
                    _upload_scene(
                        mode_product_id,
                        image_id,
                        mode_date,
                        mode_im,
                        rinfo,
                        meta))
            outs.append(out)
        return outs


def _upload_scene(product_id,image_id,date,im,rinfo,meta):
    dl_img=Image(
        product_id=Product.namespace_id(Product.namespace_id(product_id)), 
        name=image_id)
    hist=_get_histogram(im[0])
    meta['date']=date
    meta['shape']=str(im.shape)
    meta['hist']=str(hist)
    dl_img.acquired=date
    dl_img.extra_properties=meta
    dl_img.upload_ndarray(
        im,
        upload_options=None, 
        raster_meta=rinfo,
        overviews=OVERVIEWS,
        overview_resampler=OVERVIEW_RESAMPLER)
    return {
        'ACTION': 'predict',
        'SUCCESS': True,
        'image_id': image_id,
        'product_id': product_id,
        'shape': im.shape,
        'hist': hist
    }


def _get_histogram(class_band):
    cats,counts=_cats_and_counts(class_band)
    hist={ cat: cnt for cat,cnt in zip(cats,counts) }
    return { VALUE_CATEGORIES[cat]: hist.get(cat,0) for cat in range(NB_CATS) }


def _cats_and_counts(class_band):
    cats,counts=np.unique(class_band,return_counts=True)
    if isinstance(cats,np.ma.core.MaskedArray):
        cats=cats.data
    cats=[ int(c) for c  in cats ]
    counts=[ int(c) for c  in counts ]
    return cats, counts

