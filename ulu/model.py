import os
from glob import glob
from keras.models import load_model
from descarteslabs.client.services.storage import Storage
from dl_jobs.decorators import as_json, expand_args, attempt
import utils.helpers as h
from config import MODELS_DIR, DLS_ROOT


#
# CONSTANTS
#
NOTFOUND='404'


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
                dls_fetch(key,dest=path)
        else:
            path=h.model_path(filename=filename)
    return load_model(
        path, 
        custom_objects={'loss':'categorical_crossentropy'})


def dls_fetch(key,dest=None,dls_root=None,storage_root=None):
    key=h.model_key(key=key,dls_root=dls_root)
    if not dest:
        dest=h.model_storage_path(key,storage_root=storage_root)
    out=Storage().get_file(key,dest)
    return out


#
# MODEL
#
@as_json
@attempt
@expand_args
def upload(**kwargs):
    key=kwargs['key']
    filename=kwargs.get('filename')
    local_root=kwargs.get('local_root')
    dls_root=kwargs.get('dls_root')
    key=h.model_key(key=key,dls_root=dls_root)
    path=h.model_path(
        filename=filename,
        local_root=local_root)
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
def delete(**kwargs):
    key=kwargs['key']
    dls_root=kwargs.get('dls_root')
    key=h.model_key(key=key,dls_root=dls_root)
    Storage().delete(key)
    out={
        'ACTION': 'delete',
        'KEY': key,
        'SUCCESS': True
    }
    return out





