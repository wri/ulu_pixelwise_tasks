from __future__ import print_function
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from glob import glob
from tensorflow.python.keras.models import load_model
# import tensorflow.python.keras.initializers.glorot_uniform as glorot_uniform
from descarteslabs.client.services.storage import Storage
from dl_jobs.decorators import as_json, expand_args, attempt
import utils.helpers as h
from config import MODELS_DIR, DLS_ROOT


#
# CONSTANTS
#
NOTFOUND='404'
MISSING_MODEL='ERROR[ulu.model:load] model not found for key/filename {}/{}'


#
# HELPERS
#
def list(root=MODELS_DIR,ext='hd5'):
    return glob('{}/*.{}'.format(root,ext))


def dls_list(root=DLS_ROOT):
    try:
        return Storage().list(root)
    except Exception as e:
        if NOTFOUND in str(e):
            return []
        else:
            raise e


def load(key=None,filename=None,storage_root=None,path=None):
    if not path:
        if key:
            path=h.model_storage_path(key,storage_root=storage_root)
            if not os.path.isfile(path):
                if not dls_fetch(key,dest=path):
                    path=False      
        else:
            path=h.model_path(filename=filename)
    if path:
        import tensorflow as tf
        print("LOADING MODEL: ",path)
        print("TENSORFLOW VERSION: ",tf.__version__)
        mdl=load_model(
            path, 
            custom_objects={'loss':'categorical_crossentropy'})
        # custom_objects={
            #     'loss':'categorical_crossentropy',
            #     'GlorotUniform': glorot_uniform()})
        mdl.compile(loss='categorical_crossentropy',optimizer='adam')
        return mdl
    else:
        raise ValueError(MISSING_MODEL.format(key,filename))


def dls_fetch(key,dest=None,dls_root=None,storage_root=None):
    key=h.model_key(key=key,dls_root=dls_root)
    if not dest:
        dest=h.model_storage_path(key,storage_root=storage_root)
    try:
        Storage().get_file(key,dest)
        return True
    except Exception as e:
        if NOTFOUND in str(e):
            return False
        else:
            raise e    


#
# MODEL
#
@as_json
@attempt
@expand_args
def upload(key,filename,local_root=None,dls_root=None,**kwargs):
    key=h.model_key(key=key,dls_root=dls_root)
    path=h.model_path(filename=filename,local_root=local_root)
    Storage().set_file(key,path)
    out={
        'ACTION': 'upload',
        'SRC': path,
        'KEY': key,
        'SUCCESS': True
    }
    return out



@as_json
@attempt
@expand_args
def delete(key,dls_root,**kwargs):
    key=h.model_key(key=key,dls_root=dls_root)
    Storage().delete(key)
    out={
        'ACTION': 'delete',
        'KEY': key,
        'SUCCESS': True
    }
    return out





