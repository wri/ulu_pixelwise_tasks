from __future__ import print_function   
import json
from pprint import pprint
from dl_jobs.job import DLJob
from dl_jobs import catalog
import config as c
import utils.helpers as h
import utils.load as load
import utils.dlabs as dlabs
#
# DL FUNCTION ARGS
#
DATA=None
MODULES=[
    'config',
    'run',
    'utils',
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
IS_DEV=True
#
# TASKS
#
def delete(product):
    product=h.first(product)
    meta=load.meta(product,'product')
    prod_id='{}:{}'.format(c.USER,meta["name"])
    out=catalog.delete_product(prod_id)
    return json.dumps({ "method": "delete", "response": out })



def create(product):
    product=h.first(product)
    meta=load.meta(product,'product')
    out=catalog.add_product(
        name=meta['name'],
        description=meta['description'],
        resolution=meta['resolution'] )
    return json.dumps({ "method": "create", "response": out })


def add_bands():
    pass


def add_band():
    pass


def tiles(*args,**kwargs):
    job=DLJob(
        module_name='utils.product',
        method_name='tiles',
        args=args[:1],
        platform_job=False,
        modules=MODULES,
        requirements=REQUIREMENTS,
        data=DATA,
        gpus=GPUS,
        **kwargs )
    return job


