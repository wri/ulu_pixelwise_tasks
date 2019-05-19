from __future__ import print_function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from descarteslabs.client.services.catalog import Catalog
from dl_jobs.decorators import as_json, expand_args, attempt
import utils.helpers as h
import utils.load as load
import utils.dlabs as dlabs
#
# PRODUCT
#
@as_json
@attempt
@expand_args
def create(
        product_id,
        title,
        description,
        read,
        start_datetime,
        end_datetime,
        resolution,
        notes, 
        **kwargs):
    resolution="{}m".format(resolution)
    notes=h.notes(notes)
    out=Catalog().add_product(
        product_id,
        title,
        description,
        read,
        start_datetime,
        end_datetime,
        resolution,
        notes )
    return out



@as_json
@attempt
@expand_args
def delete(product_id,cascade):
    out=Catalog().remove_product(
        product_id=product_id, 
        cascade=cascade )
    return out



#
# BANDS
#
@as_json
@attempt
@expand_args
def add_bands(bands_kwargs_list):
    out=[]
    for kwargs in bands_kwargs_list:
        out.append(add_band(kwargs))
    return out 



@as_json
@attempt
@expand_args
def add_band(**kwargs):
    out=Catalog().add_band( **kwargs )
    return out



@as_json
@attempt
@expand_args
def remove_bands(*args):
    out=[]
    for kwargs in args:
        out.append(remove_band(kwargs))
    return out 



@as_json
@attempt
@expand_args
def remove_band(**kwargs):
    product_id=kwargs['product_id']
    name=kwargs['name']
    out=Catalog().remove_band( product_id, name )
    if not out:
        out={ 
            'ACTION': 'remove_band', 
            'PRODUCT': product_id,
            'BAND': name,
            'SUCCESS': True }
    return out

