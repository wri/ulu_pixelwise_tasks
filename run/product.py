import json
from pprint import pprint
from dl_jobs import catalog
import config as c
import utils.helpers as h
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
#
# TASKS
#
def delete(product):
    product=h.first(product)
    meta=c.product_meta(product,'product')
    prod_id=f'{c.USER}:{meta["name"]}'
    out=catalog.delete_product(prod_id)
    return json.dumps({ "method": "delete", "response": out })



def create(product):
    product=h.first(product)
    meta=c.product_meta(product,'product')
    out=catalog.add_product(
        name=meta['name'],
        description=meta['description'],
        resolution=meta['resolution'] )
    return json.dumps({ "method": "create", "response": out })

