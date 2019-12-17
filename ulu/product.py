from __future__ import print_function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from descarteslabs.catalog import Product
from descarteslabs.catalog import SpectralBand, MicrowaveBand, MaskBand
from descarteslabs.catalog import ClassBand, GenericBand
from dl_jobs.decorators import as_json, expand_args, attempt


NO_DELETE_MESSAGE=(
    "Deletion has been disabled to prevent "
    "accidental removal of products. "
    "Delete product through the web-ui or "
    "by running the following command:  "
    "out=Catalog().remove_product(product_id=product_id,cascade=cascade)  "
)

SPECTRAL='spectral'
MICROWAVE='microwave'
MASK='mask'
CLASS='class'


#
# PRODUCT
#
@as_json
@attempt
@expand_args
def create(**kwargs):
    # return Product(**kwargs).save()
    ident=kwargs.pop('id')
    p=Product(id=ident)
    p=_update_object(p,kwargs)
    return p.save()


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
    return [ add_band(b) for b in bands ] 


@as_json
@attempt
@expand_args
def add_band(**kwargs):
    band_type=kwargs.pop('type',None)
    band_name=kwargs.pop('name')
    product_id=Product.namespace_id(kwargs.pop('product_id'))
    band=_dl_band(band_type)
    b=band(name=band_name,product_id=product_id)
    b=_update_object(b,kwargs)
    return b.save()


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
    band_type=kwargs.pop('type',None)
    band_name=kwargs.pop('name')
    product_id=Product.namespace_id(kwargs.pop('product_id'))
    namespaced_band_name=f'{product_id}:{band_name}'
    b=band.get(f'{product_id}:{band_name}')
    b=_update_object(b,kwargs)
    return b.save()




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
    # product_id=kwargs['product_id']
    # name=kwargs['name']
    # out=Catalog().remove_band( product_id, name )
    # if not out:
    #     out={ 
    #         'ACTION': 'remove_band', 
    #         'PRODUCT': product_id,
    #         'BAND': name,
    #         'SUCCESS': True }
    # return out
    raise NotImplementedError('TODO: remove band with oo catalog')




#
# INTERNAL 
#
def _dl_band(band_type):
    if band_type==CLASS:
        return ClassBand
    elif band_type==SPECTRAL:
        return SpectralBand
    elif band_type==MICROWAVE:
        return MicrowaveBand
    elif band_type==MASK:
        return MaskBand
    else:
        return GenericBand


def _update_object(obj,data):
    for key,value in data.items():
        setattr(obj,key,value)
    return obj






