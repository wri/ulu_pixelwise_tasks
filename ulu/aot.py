from __future__ import print_function
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from glob import glob
from descarteslabs.client.services.storage import Storage
import aot.numba_window_cloud_scores as nwcs
from dl_jobs.decorators import as_json, expand_args, attempt


#
# HELPERS
#
def upload(key,path,dls_root=None,**kwargs):
    Storage().set_file(key,path)
    out={
        'ACTION': 'upload',
        'SRC': path,
        'KEY': key,
        'SUCCESS': True
    }
    return out


#
# JOB METHODS
#
@as_json
@attempt
@expand_args
def window_cloud_scores(dls_root):
    output_dir=nwcs.cc.output_dir
    output_file=nwcs.cc.output_file
    nwcs.cc.compile()
    upload_data=upload(
        key='{}/{}'.format(dls_root,output_file),
        path='{}/{}'.format(output_dir,output_file),
        dls_root=dls_root)
    return { 
        'aot': 'window_cloud_scores',
        'output_dir': output_dir,
        'output_file': output_file,
        'upload': upload_data
    }



@as_json
@attempt
@expand_args
def fetch(key,filename,local_root=None,dls_root=None,**kwargs):
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


