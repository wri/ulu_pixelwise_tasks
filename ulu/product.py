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
def delete(**kwargs):
    out=Catalog().remove_product(
        kwargs['product_id'], 
        add_namespace=True, 
        cascade=kwargs['cascade'] )
    return out



PRODUCT_KWARGS=[
    'product_id',
    'title',
    'description',
]
@as_json
@attempt
@expand_args
def create(**kwargs):
    prod_kwargs=h.extract_kwargs(kwargs,PRODUCT_KWARGS)
    start,end=h.start_end_datetimes(kwargs.get('dates'))
    prod_kwargs['resolution']="{}m".format(kwargs['resolution'])
    prod_kwargs['start_datetime']=start
    prod_kwargs['end_datetime']=end
    prod_kwargs['notes']=h.notes(kwargs,exclude=PRODUCT_KWARGS)
    out=Catalog().add_product( **prod_kwargs )
    return out



#
# BANDS
#
@as_json
@attempt
@expand_args
def add_bands(*args):
    out=[]
    for kwargs in args:
        kwargs['return_as_dict']=True
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
        kwargs['return_as_dict']=True
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

