from __future__ import print_function
import math
import json
import copy
from pprint import pprint
import numpy as np
import mproc
import dl_jobs.catalog as catalog
from dl_jobs.job import DLJob
import ulu.predict as ulu_pred
import utils.helpers as h
import utils.load as load
import utils.dlabs as dlabs

MAX_THREADPOOL_PROCESSES=32

#
# CONSTANTS
#
TEST_WARN_TMP="TEST-MODE: executing sing task [{}]"
CONFIG_METHODS=[
    'test',
    'tasks'
]

#
# DL FUNCTION ARGS
#
DATA=None
MODULES=[
    'config',
    'utils',
    'ulu',
    'run',
    'dl_jobs'
]
REQUIREMENTS=[
    'descarteslabs[complete]>=0.18',
    'numpy==1.16.3',
    'rasterio==1.0.22',
    'requests==2.21.0',
    'matplotlib==2.2.3',
    'keras==2.1.2',
    'tensorflow==1.1.0'
]
GPUS=None



#
# TASKS
#
def task(*args,**kwargs):
    product=args[0]
    limit=kwargs.get('limit',None)
    date_index=kwargs.get('date',None)
    region_index=kwargs.get('region',None)
    args_list=ulu_pred.args_list(
        product,
        date_index=date_index,
        region_index=region_index)
    if limit:
        args_list=args_list[:limit]
    job=DLJob(
        module_name='ulu.prediction',
        method_name='predict',
        args_list=args_list,
        modules=MODULES,
        requirements=REQUIREMENTS,
        data=DATA,
        gpus=GPUS,
        **kwargs )
    return job


def predict(*args):
    print('\n'*5)
    print('-'*100)
    print(args)
    # return {'keys':args[0].keys(),'len':len(args)}
    return json.dumps({'keys':type(args),'len':len(args)})


