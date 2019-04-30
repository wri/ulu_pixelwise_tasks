import descarteslabs as dl
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
    resp=dl.Catalog().remove_product(
        kwargs['product_id'], 
        add_namespace=True, 
        cascade=True )
    return resp



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
    resp=dl.Catalog().add_product( **prod_kwargs )
    return resp



#
# BANDS
#