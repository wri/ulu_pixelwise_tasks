import re
import numpy as np
#
# MAIN
#
EPS=1e-8



def default_cloud_score(clouds):
    return clouds.mean()


def cloud_score(im,window,pad='window'):
    image=preprocess(im)
    mask=cloud_mask(image,bands_first=True)
    scores=map_cloud_scores(mask,window,pad=pad)
    return mask, scores


def preprocess(im):
    """
    - drop alpha
    - rescale
    - clip: 0,1
    """
    return (im[:-1]/10000.0).clip(0.0,1.0)


def spectral_index(img,b1,b2,eps=EPS,bands_first=False):
    if bands_first:
        b1=img[b1]
        b2=img[b2]
    else:
        b1=img[:,:,b1]
        b2=img[:,:,b2]
    return np.divide(b1-b2,b1+b2+eps).clip(-1.0,1.0)


def cloud_mask(X,bands_first=False):
    if bands_first:
        L2 = X[1,:,:]
    else:
        L2 = X[:,:,1]
    index = (L2 >= 0.20)
    grey = spectral_index(X,1,0,bands_first=bands_first)
    index = np.logical_and(index, (abs(grey) < 0.2))    
    grey = spectral_index(X,2,1,bands_first=bands_first)
    index = np.logical_and(index, (abs(grey) < 0.2))
    return index


def map_cloud_scores(
        clouds,
        window,
        scorer=default_cloud_score,
        pad='window',
        noise=100):
    r=int(window/2)
    if pad is 'window':
        pad=r
    assert clouds.ndim==2
    assert clouds.shape[0]==clouds.shape[1]
    rows,cols=clouds.shape
    score_map=np.zeros(clouds.shape, dtype='float32')
    for j in range(r,rows-r):
        if noise and (not j%noise): print('--',j)
        for i in range(r,cols-r):
            clouds_window=clouds[j-r:j+r+1,i-r:i+r+1]
            window_score=scorer(clouds_window)
            score_map[j,i]=window_score
    if pad:
        score_map[:pad,:] = -1.0; score_map[-pad:,:] = -1.0
        score_map[:,:pad] = -1.0; score_map[:,-pad:] = -1.0
    return score_map




#
#
#
#
#
#
#
#
#

def water_mask(*args):
    # water_mask = util_imagery.calc_water_mask(im[:-1], bands_first=True)
    # water_mask[blank_mask] = 255    
    pass


def image_id(products,product_name,scene,tile_key=None):
    s_id=scene.properties.id
    name=next(re.sub(f'^{p}',product_name,s_id) for p in products if p in s_id)
    if tile_key:
        name=f'{name}:{tile_key}'
    return name


def predict(arr):
    alpha_mask=arr[-1].astype(bool)
    mask=np.invert(alpha_mask)
    generator=ImageSampleGenerator(im,pad=tile_pad,look_window=17,prep_image=True)
    predictions=network.predict_generator(
        generator, 
        steps=generator.steps, 
        verbose=0,
        use_multiprocessing=False,
        max_queue_size=1,
        workers=1,)
    predictions=predictions.reshape((tile_size,tile_size),order='F')
    return predictions, mask


def lulc(predictions,blank_mask):
    Yhat = predictions.argmax(axis=-1)
    lulc = np.zeros((tile_side,tile_side),dtype='uint8')
    lulc.fill(255)
    lulc[tile_pad:-tile_pad,tile_pad:-tile_pad] = Yhat[:,:]
    lulc[blank_mask]=255
    return lulc


def product_image(lulc,predictions,cloud_mask,water_mask):
    """ combine these together """
    pass

