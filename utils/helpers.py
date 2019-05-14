from __future__ import print_function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import os
import re
from datetime import datetime
from copy import deepcopy
import pickle
import functools
import operator
import numpy as np
from config import REGIONS_DIR, WINDOW_PADDING
from config import DLS_ROOT, MODELS_DIR, STORAGE_DIR, CONFG_LIST_DIR

#
# CONSTANTS
#
EPS=1e-8
TILES_TMPL='{}/{}/tiles-{}:{}:{}.p'
TILE_KEYS_TMPL='{}/{}/tile_keys-{}:{}:{}.p'
EXTRACT_DATE_RGX=r'\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])'
DEFAULT_DATE='9999-12-31'
YYYY_MM_DD='%Y-%m-%d'
AS_DATETIME=False
FALSEY=['false','none','no','null','f','n','0']
CONFIG_LIST_TMPL="{}_{}:{}"

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
# PATHS/NAMES/VALUES
#
def tiles_path(region,res,size,pad):
    return TILES_TMPL.format(
            REGIONS_DIR,
            region.lower(),
            res,size,pad )


def tile_keys_path(region,res,size,pad):
    return TILE_KEYS_TMPL.format(
            REGIONS_DIR,
            region.lower(),
            res,size,pad )


def model_name(name=None,filename=None,key=None):
    if not name:
        base=filename or key
        name=os.path.splitext(os.path.basename(base))[0]
    return name


def model_key(key,dls_root=None):
    if dls_root is None: 
        dls_root=DLS_ROOT
    if dls_root and (dls_root not in key):
        key='{}/{}'.format(dls_root,key)
    return key


def model_storage_path(key,storage_root=None):
    if storage_root is None: 
        storage_root=STORAGE_DIR
    name=os.path.basename(key)
    return "{}/{}".format(storage_root,name)


def model_path(filename,local_root=None):
    if local_root is None:
        local_root=MODELS_DIR
    if local_root:
        filename='{}/{}'.format(local_root,filename)
    return filename


def config_list_path(config_list_name,product=None,size=None,window=None):
    if config_list_name: 
        if config_list_name is True:
            config_list_name=CONFIG_LIST_TMPL.format(product,size,window)
        return "{}/{}.p".format(CONFG_LIST_DIR,config_list_name)


def product_id(name,owner):
    if (":" in name) or (not owner):
        return name
    else:
        return '{}:{}'.format(owner,name)


def product_title(name,title):
    if title:
        return title
    else:
        return name.upper()


def notes(notes_dict,exclude=[]):
    note=""
    exclude=map(str.upper,exclude)
    for key in notes_dict.keys():
        keyup=key.upper()
        if keyup not in exclude:
            note+="{}: {}    \n".format(keyup,notes_dict[key])
    return note
    

def image_id(prods,pname,sid,tkey=None):
    """
    Args:
        prods=products
        pname=product_name
        sid=scene_id
        tkey=tile_key
    """
    name=next(re.sub('^{}'.format(p),pname,sid) for p in prods if p in sid)
    if tkey:
        name='{}:{}'.format(name,tkey)
    return name

    
#
# META/CONFIG
#
def resolution_size_padding(meta):
    res=strip_to_int(meta['product']['resolution'],'m')
    run_cfig=meta['run']
    size=run_cfig['size']
    pad=get_padding(run_cfig['pad'],run_cfig['window'])
    return res, size, pad


def window(x,j,i,r,bands_first=True):
    """ UrbanLandUse: utils_rasters """
    j,i,r=int(j),int(i),int(r)
    if bands_first:
        w=x[:,j-r:j+r+1,i-r:i+r+1]
    else:
        w=x[j-r:j+r+1,i-r:i+r+1,:]
    return w


def get_padding(pad,window):
    if pad==WINDOW_PADDING:
        return int(window/2)
    else:
        return pad


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
        obj=pickle.load(file, encoding='latin1')
    return obj



#
# PYTHON
#
def is_str(value):
    if isinstance(value,str):
        return True
    else:
        try: 
            is_a_str=isinstance(out,unicode)
        except:
            is_a_str=False
        return is_a_str


def truthy(value):
    if isinstance(value,bool) or isinstance(value,int) or (value is None):
        return value
    elif isinstance(value,str):
        value=value.lower()
        return value not in FALSEY
    else:
        raise ValueError('truthy: value must be str,int,bool')


def first(value):
    if isinstance(value,tuple) or isinstance(value,list):
        return value[0]
    else:
        return value


def expand_dict_list(key,values,**kwargs):
    return [dict(key=v,**deepcopy(kwargs)) for v in values]


def extract_list(lst,index):
    if (index is None) or (index is 'None'):
        return lst
    else:
        return [lst[int(index)]]


def extract_date(dated_str,default=DEFAULT_DATE,as_datetime=AS_DATETIME):
    date_match=re.search(EXTRACT_DATE_RGX,dated_str)
    if date_match:
        date=dated_str[date_match.start():date_match.end()]
    else:
        date=DEFAULT_DATE
    if as_datetime:
        return datetime.strptime(date,YYYY_MM_DD)
    else:
        return date


def start_end_datetimes(dates,as_datetime=False):
    starts=[datetime.strptime(d['start'],YYYY_MM_DD) for d in dates]
    ends=[datetime.strptime(d['end'],YYYY_MM_DD) for d in dates]
    starts.sort()
    ends.sort()
    start=starts[0]
    end=ends[-1]
    if not as_datetime:
        start,end=start.strftime(YYYY_MM_DD),end.strftime(YYYY_MM_DD)
    return start, end


def extract_kwargs(kwargs,arg_list,required=True,default=None):
    if required:
        return { a:kwargs[a] for a in arg_list }
    else:
        return { a:kwargs.get(a,default) for a in arg_list }


def flatten_list(a):
    return functools.reduce(operator.iconcat, a, [])


def strip_to_int(value,strip):
    value=re.sub(strip,'',str(value))
    return int(value)


