from __future__ import print_function
import numpy as np
#
# CONSTANTS
#
EPS=1e-8


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
# I/O
#
def write(*args,**kwargs):
    pass



#
# PYTHON
#
def first(value):
    if isinstance(value,tuple) or isinstance(value,list):
        return value[0]
    else:
        return value


