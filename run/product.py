from __future__ import print_function   
import json
from pprint import pprint
from dl_jobs import catalog
import config as c
import utils.helpers as h
import utils.load as load
#
# DL FUNCTION ARGS
#
DATA=None
MODULES=[
    'run',
    'dl_jobs'
]
REQUIREMENTS=[
    'descarteslabs[complete]>=0.17.3',
    'numpy==1.16.2',
    'rasterio==1.0.22',
    'affine==2.2.2'
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

