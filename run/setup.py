from __future__ import print_function
import warnings
import run.product as product
import run.model as model
import utils.load as load
from dl_jobs.job import DLJob
warnings.filterwarnings("ignore", category=DeprecationWarning)

ALL='all'

def task(*args,**kwargs):
    job_prod=product.create(*args,**kwargs)    
    job_bands=product.add_bands(*args,**kwargs)    
    job_model=model.upload(*args,**kwargs)
    return [ job_prod, job_bands, job_model ]


def tiles(*args,**kwargs):
    """ save arglist for fixed nb of tiles best cloudscores """
    product=args[0]
    region=args[1]
    force=kwargs.get('force',False)
    noisy=kwargs.get('noisy',True)
    limit=kwargs.get('limit',False)
    if limit: 
        limit=int(limit)
    if region==ALL:
        regions=load.meta(product,'run','regions')
        jobs=[]
        for region in regions:
            jobs.append(_tiles_job(product,region,force,noisy,limit))
        return jobs
    else:
        return _tiles_job(product,region,force,noisy,limit)


def _tiles_job(product,region,force,noisy,limit):
    kwargs={
        'product': product,
        'region': region,
        'limit': limit,
        'force': force }
    job=DLJob(
        module_name='ulu.setup',
        method_name='save_tiles',
        kwargs=kwargs,
        platform_job=False,
        noisy=noisy,
        log=False )
    return job