from __future__ import print_function
import warnings
import run.product as product
import run.model as model
warnings.filterwarnings("ignore", category=DeprecationWarning)



def task(*args,**kwargs):
    job_prod=product.create(*args,**kwargs)    
    job_bands=product.add_bands(*args,**kwargs)    
    job_model=model.upload(*args,**kwargs)
    return [ job_prod, job_bands, job_model ]



def tiles(*args,**kwargs):
    """ save arglist for fixed nb of tiles best cloudscores """
    product=args[0]
    hard_limit=kwargs.get('hard_limit',0)
    if hard_limit: 
        hard_limit=int(hard_limit)
        limit=hard_limit
    else:
        limit=kwargs.get('limit',False)
        if limit: limit=int(limit)
    date_index=kwargs.get('date',None)
    region_index=kwargs.get('region',None)
    args_list=info.config_list(
        product,
        date_index=date_index,
        region_index=region_index,
        limit=limit,
        nb_scenes=nb_scenes )
