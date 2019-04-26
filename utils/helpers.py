from __future__ import print_function
import pickle
import functools
import operator
import numpy as np
from config import REGIONS_DIR
#
# CONSTANTS
#
EPS=1e-8
TILES_TMPL='{}/{}/tiles-{}:{}:{}.p'

#
# IMAGE HELPERS
#
def crop(arr,size,bands_first=True):
    if size:
        if bands_first:
            return arr[size:-size,size:-size]
        else:
            return arr[:,size:-size,size:-size]
    else:
        return arr


def spectral_index(im,b1,b2,eps=EPS,bands_first=False):
    if bands_first:
        b1=im[b1]
        b2=im[b2]
    else:
        b1=im[:,:,b1]
        b2=im[:,:,b2]
    return np.divide(b1-b2,b1+b2+eps).clip(-1.0,1.0)



#
# PATHS
#
def tiles_path(region,res,size,pad):
    return TILES_TMPL.format(
            REGIONS_DIR,
            region.lower(),
            res,size,pad )


#
# I/O
#
def save_pickle(obj,path):
    """ save object to pickle file
    """    
    with open(path,'wb') as file:
        pickle.dump(obj,file,protocol=pickle.HIGHEST_PROTOCOL)


def read_pickle(path):
    """ read pickle file
    """    
    with open(path,'rb') as file:
        obj=pickle.load(file)
    return obj



#
# PYTHON
#
def first(value):
    if isinstance(value,tuple) or isinstance(value,list):
        return value[0]
    else:
        return value


def flatten_list(a):
    return functools.reduce(operator.iconcat, a, [])

