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



def prep_args(*args,**kwargs):
    """ save arglist for fixed nb of tiles best cloudscores """
    pass
