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
from config import REGIONS_DIR, WINDOW_PADDING, DLS_ROOT, CONFG_LIST_DIR
from config import SCENES_DIR, TILES_DIR, MODELS_DIR, STORAGE_DIR


#
# CONSTANTS
#
EPS=1e-8
TILES_SCENES_TMPL='{}/{}-{}:{}:{}'
EXTRACT_DATE_RGX=r'\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])'
DEFAULT_DATE='9999-12-31'
YYYY_MM_DD='%Y-%m-%d'
AS_DATETIME=False
CONFIG_LIST_TMPL="{}_{}:{}"
SEP_RGX=r'[_\-\.\,/\ ]'

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


def spectral_index(im,b1,b2,eps=EPS,bands_first=False,is_stack=False):
    if is_stack:
        if bands_first:
            b1=im[:,b1]
            b2=im[:,b2]
        else:
            b1=im[:,:,:,b1]
            b2=im[:,:,:,b2]
    else:
        if bands_first:
            b1=im[b1]
            b2=im[b2]
        else:
            b1=im[:,:,b1]
            b2=im[:,:,b2]
    return np.divide(b1-b2,b1+b2+eps).clip(-1.0,1.0)


def mode(a, axis=0):
    """ https://stackoverflow.com/a/12399155/607528
    """
    scores = np.unique(np.ravel(a))
    testshape = list(a.shape)
    testshape[axis] = 1
    oldmostfreq = np.zeros(testshape)
    oldcounts = np.zeros(testshape)

    for score in scores:
        template = (a == score)
        counts = np.expand_dims(np.sum(template, axis),axis)
        mostfrequent = np.where(counts > oldcounts, score, oldmostfreq)
        oldcounts = np.maximum(counts, oldcounts)
        oldmostfreq = mostfrequent

    return mostfrequent, oldcounts


#
# PATHS/NAMES/VALUES
#
def tiles_path(
        region,
        res,
        size,
        pad,
        version=None,
        limit=None):
    path=TILES_SCENES_TMPL.format(
            TILES_DIR,
            region.lower(),
            res,size,pad )
    if version:
        path='{}-v{}'.format(path,version)
    if limit:
        path='{}-lim{}'.format(path,limit)
    return '{}.p'.format(path)


def scenes_path(tiles_path,nb_scenes,start_date,end_date):
    name=re.sub(r'\.p$','',os.path.basename(tiles_path))
    start_date=int(re.sub(SEP_RGX,'',start_date))
    end_date=int(re.sub(SEP_RGX,'',end_date))
    path=TILES_SCENES_TMPL.format(
        SCENES_DIR,
        name,
        nb_scenes,
        start_date,
        end_date )
    return '{}.ndjson'.format(path)


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
    if name:
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
        sid=scene_id or list of scene_ids
        tkey=tile_key
    """
    if isinstance(sid,list):
        slen=len(sid)
        sid=sid[0]
    else:
        slen=False
    ps=[p for p in prods if p in sid]
    name=next(re.sub('^{}'.format(p),pname,sid) for p in prods if p in sid)
    if slen:
        name='{}+{}'.format(name,slen)
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
def sortby(by,*others):
    return zip(*sorted(list(zip(by,*others))))



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


def extract_kwargs(kwargs,arg_list,required=False,default=None):
    if required:
        return { a:kwargs[a] for a in arg_list }
    else:
        return { a:kwargs.get(a,default) for a in arg_list }


def flatten_list(a):
    return functools.reduce(operator.iconcat, a, [])


def strip_to_int(value,strip):
    value=re.sub(strip,'',str(value))
    return int(value)


def sorted_dates(dates,as_str=True,strfmt='%Y-%m-%d'):
    dates=[parse_date(d) for d in dates]
    dates.sort()
    if as_str:
        dates=[d.strftime(strfmt) for d in dates]
    return dates


def mid_date(date_1,date_2,as_str=True,strfmt='%Y-%m-%d'):
    date_1,date_2=parse_date(date_1), parse_date(date_2)
    date=date_1+(date_2-date_1)/2
    if as_str:
        date=date.strftime(strfmt) 
    return date


def max_min_dates(dates,as_str=True,strfmt='%Y-%m-%d'):
    dates=sorted_dates(dates,as_str=as_str,strfmt=strfmt)
    return min_date, max_date
        

def parse_date(date):
    if isinstance(date,datetime):
        return date
    else:
        if isinstance(date,int):
            date=str(date)
            parts=(int(d[:4]),int(d[4:6]),int(d[6:]))
        elif isinstance(date,str):
            parts=[int(d) for d in date.split('-')]
        elif isinstance(date,[tuple,list]):
            parts=date
        return datetime(*parts)


