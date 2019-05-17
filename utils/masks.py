from __future__ import print_function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import numpy as np
from utils.generator import WINDOW_PADDING, preprocess
import utils.helpers as h

#
# CLOUDS
#
def default_cloud_score(clouds):
    return clouds.mean()


def cloud_score(im,window,pad='window',noise=None):
    image=preprocess(im)
    mask=cloud_mask(image,bands_first=True)
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


def map_cloud_scores(
        clouds,
        window,
        scorer=default_cloud_score,
        pad=WINDOW_PADDING,
        noise=None):
    pad=h.get_padding(pad,window)
    r=int(window/2)
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


#
# water
#
def calc_water_mask(im,idx_green=1,idx_nir=3,threshold=0.15,bands_first=False):
    if bands_first:
        assert im.shape[0]==6
    else:
        assert im.shape[2]==6
    ndwi=h.spectral_index(im,idx_green,idx_nir,bands_first=bands_first)
    return ndwi > threshold


def water_mask(arr,mask=None):
    water_mask=calc_water_mask(arr[:-1],bands_first=True)
    if mask is not None:
        crp=int((water_mask.shape[1]-mask.shape[1])/2)
        water_mask=h.crop(water_mask,crp)
        water_mask[mask]=255    
    return water_mask



#
# OTHER
#
def blank_mask(arr,crp=None):
    blank_mask=np.invert(arr[-1].astype(bool))
    if crp:
        blank_mask=h.crop(blank_mask,crp)
    return blank_mask


