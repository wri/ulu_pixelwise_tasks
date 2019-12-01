from __future__ import print_function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from descarteslabs.client.services.catalog import Catalog
from dl_jobs.decorators import as_json, expand_args, attempt
import utils.helpers as h
import utils.load as load
import utils.dlabs as dlabs


NO_DELETE_MESSAGE=(
    "Deletion has been disabled to prevent "
    "accidental removal of products. "
    "Delete product through the web-ui or "
    "by running the following command:  "
    "out=Catalog().remove_product(product_id=product_id,cascade=cascade)  "
)


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
    if isinstance(start_datetime,list):
        start_datetime=start_datetime[0]
        end_datetime=start_datetime[-1]
    resolution="{}m".format(resolution)
    out=Catalog().add_product(
        product_id=product_id,
        title=title,
        description=description,
        read=read,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        resolution=resolution,
        notes=notes )
    return out



@as_json
@attempt
@expand_args
def delete(product_id,cascade):
    raise ValueError(NO_DELETE_MESSAGE)



#
# BANDS
#
@as_json
@attempt
@expand_args
def add_bands(*bands):
    out=[ add_band(b) for b in bands ]
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
def update_bands(*bands):
    out=[ update_band(b) for b in bands ]
    return out 



@as_json
@attempt
@expand_args
def update_band(**kwargs):
    out=Catalog().change_band( **kwargs )
    return out



@as_json
@attempt
@expand_args
def remove_bands(*bands):
    out=[ remove_band(b) for b in bands ]
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

