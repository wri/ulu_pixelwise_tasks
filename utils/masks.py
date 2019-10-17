from __future__ import print_function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import numpy as np
from numba import njit
from utils.generator import WINDOW_PADDING, preprocess
import utils.helpers as h
#
# CLOUDS
#
def default_cloud_score(clouds):
    return clouds.mean()


def cloud_score(im,window,pad='window',noise=None,bands_first=False):
    im=preprocess(im,bands_last=(not bands_first))
    mask=cloud_mask(im,bands_first=bands_first)
    scores=map_cloud_scores(mask,window,pad=pad,noise=noise)
    return mask, scores


def cloud_mask(im,bands_first=False,threshold=0.20):
    if bands_first:
        L2=im[1,:,:]
    else:
        L2=im[:,:,1]
    index=(L2 >= threshold)
    grey=h.spectral_index(im,1,0,bands_first=bands_first)
    index=np.logical_and(index, (abs(grey) < threshold))    
    grey=h.spectral_index(im,2,1,bands_first=bands_first)
    return np.logical_and(index, (abs(grey) < threshold))


def stack_cloud_mask(im,bands_first=False,threshold=0.20):
    if bands_first:
        L2=im[:,1,:,:]
    else:
        L2=im[:,:,:,1]
    index=(L2 >= threshold)
    grey=h.spectral_index(im,1,0,bands_first=bands_first,is_stack=True)
    index=np.logical_and(index, (abs(grey) < threshold))    
    grey=h.spectral_index(im,2,1,bands_first=bands_first,is_stack=True)
    return np.logical_and(index, (abs(grey) < threshold))



def image_cloud_score(im,bands_first=False,threshold=0.20):
    im=preprocess(im)
    im=cloud_mask(im,bands_first=bands_first,threshold=threshold)
    return im.mean()


def slow_map_cloud_scores(
        clouds,
        window,
        scorer=default_cloud_score,
        pad=WINDOW_PADDING,
        noise=None):
    pad=h.get_padding(pad,window)
    r=int(window/2)
    print(clouds.shape)
    assert clouds.ndim==2
    assert clouds.shape[0]==clouds.shape[1]
    rows,cols=clouds.shape
    score_map=np.empty(clouds.shape, dtype='float32')
    score_map.fill(-1)
    for j in range(r,rows-r):
        if noise and (not j%noise): print('--',j)
        for i in range(r,cols-r):
            clouds_window=clouds[j-r:j+r+1,i-r:i+r+1]
            window_score=scorer(clouds_window)
            score_map[j,i]=window_score
    return score_map


def map_cloud_scores(
        clouds,
        window,
        scorer=None,
        pad=WINDOW_PADDING,
        noise=None):
    """
    * scorer/noise args temporarily kept for compatibility
    * wraps njit methods to set padding and to pad
    """
    pad=h.get_padding(pad,window)
    scores=_njit_cloud_score(clouds,window)
    return np.pad(np.array(scores),(pad,pad),'constant',constant_values=-1)


@njit(cache=False)
def _njit_cloud_score(clouds,window):
    r=int(window/2)
    rows,cols=clouds.shape
    score_map=np.full((rows,cols),-1)
    scores=[]
    for j in range(r,rows-r):
        score_cols=[]
        for i in range(r,cols-r):
            clouds_window=clouds[j-r:j+r+1,i-r:i+r+1]
            score_cols.append(clouds_window.mean())
        scores.append(score_cols)
    return np.array(scores)  


#
# water
#
def calc_water_mask(im,idx_green=1,idx_nir=3,threshold=0.15,bands_first=False):
    ndwi=h.spectral_index(im,idx_green,idx_nir,bands_first=bands_first)
    return ndwi > threshold


def water_mask(arr,mask=None,bands_first=False):
    water_mask=calc_water_mask(arr,bands_first=bands_first)
    if mask is not None:
        crp=int((water_mask.shape[1]-mask.shape[1])/2)
        water_mask=h.crop(water_mask,crp)
        water_mask[mask]=255    
    return water_mask



#
# OTHER
#
def blank_mask(arr,crp=None,bands_first=False):
    if bands_first:
        arr=arr[-1]
    else:
        arr=arr[:,:,-1]
    blank_mask=np.invert(arr.astype(bool))
    if crp:
        blank_mask=h.crop(blank_mask,crp)
    return blank_mask


