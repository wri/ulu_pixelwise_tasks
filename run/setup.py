from __future__ import print_function
import os
import warnings
import run.product
import run.model
import utils.helpers as h
import utils.load as load
import ulu.info as info
from dl_jobs.job import DLJob
import dl_jobs.helpers as dh
warnings.filterwarnings("ignore", category=DeprecationWarning)
#
# CONSTANTS
#
ALL='all'
TILES_EXIST='ERROR[run.setup.tiles]: tile_set ({}) exists. use force=True to overwrite'


#
# WORKER SETUP
#
MODULES=[
    'config',
    'utils',
    'ulu.setup',
    'dl_jobs'
]



#
# PUBLIC
#
def product(*args,**kwargs):
    """ 
    1. Create DLProduct
    2. Add Bands to DLProduct
    3. Upload model to DLStorage
    """
    job_prod=run.product.create(*args,**kwargs)    
    job_bands=run.product.add_bands(*args,**kwargs)    
    job_model=run.model.upload(*args,**kwargs)
    return [ job_prod, job_bands, job_model ]


def tiles(product,region=ALL,**kwargs):
    """ save tiles """
    force=dh.truthy(kwargs.get('force',False))
    noisy=dh.truthy(kwargs.get('noisy',True))
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


#
# INTERNAL
#
def _tiles_job(product,region,force,noisy,limit):
    path=info.get_tiles_path(product,region,limit)
    if os.path.isfile(path) and (not force):
        raise ValueError( TILES_EXIST.format(path) )
    else:
        kwargs={
            'path': path,
            'product': product,
            'region': region,
            'limit': limit }
        job=DLJob(
            module_name='ulu.setup',
            method_name='save_tiles',
            kwargs=kwargs,
            platform_job=False,
            noisy=noisy,
            log=False )
        return job

