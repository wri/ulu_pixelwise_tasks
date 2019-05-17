from __future__ import print_function
import os
import warnings
import run.product
import run.model
import utils.helpers as h
import utils.load as load
import ulu.info as info
from dl_jobs.job import DLJob
warnings.filterwarnings("ignore", category=DeprecationWarning)


#
# CONSTANTS
#
ALL='all'
TILES_EXIST='ERROR[run.setup.tiles]: tile_set ({}) exists. use force=True to overwrite'
SCENES_EXIST='ERROR[run.setup.scenes]: scenes_set ({}) exists. use force=True to overwrite'
TILES_MUST_EXIST='ERROR[ulu.scenes]: must save tiles before scenes. ==> run.setup.tiles'


#
# WORKER SETUP
#
MODULES=[
    'config',
    'utils',
    'ulu',
    'mproc',
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
    force=h.truthy(kwargs.get('force',False))
    noisy=h.truthy(kwargs.get('noisy',True))
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


def scenes(product,region=ALL,**kwargs):
    """ save scenes """
    force=h.truthy(kwargs.get('force',False))
    noisy=h.truthy(kwargs.get('noisy',True))
    limit=kwargs.get('limit',False)
    if limit: 
        limit=int(limit)
    if region==ALL:
        regions=load.meta(product,'run','regions')
        jobs=[]
        for region in regions:
            jobs.append(_scenes_job(product,region,force,noisy,limit))
        return jobs
    else:
        return _scenes_job(product,region,force,noisy,limit)



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


def _scenes_job(product,region,force,noisy,limit ):
    tiles_path=info.get_tiles_path( product,region,limit )
    if not os.path.isfile(tiles_path):
        raise ValueError( TILES_MUST_EXIST.format(tiles_path) )
    else:
        cfig=load.meta(product,'run')
        nb_scenes=cfig['nb_scenes']
        start_date=cfig['start_date']
        end_date=cfig['end_date']
        path=h.scenes_path(
            tiles_path,
            nb_scenes,
            start_date,
            end_date)
        if os.path.isfile(path):
            if force:
                os.remove(path) 
            else:
                raise ValueError( SCENES_EXIST.format(path) )
        tile_keys=h.read_pickle(tiles_path)
        kwargs=info.get_scenes_kwargs(product,region,limit)
        args_list=[ h.copy_update(kwargs,'tile_key',t) for t in tile_keys ]
        job=DLJob(
            module_name='ulu.setup',
            method_name='save_scenes',
            args_list=args_list,
            save_results=path,
            modules=MODULES,
            gpus=None,
            platform_job=True,
            noisy=noisy )
        return job

