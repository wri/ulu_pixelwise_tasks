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
SCENES_EXIST='ERROR[run.setup.scenes]: scenes_set ({}) exists. use force=True to overwrite'
TILES_REQUIRED='ERROR[ulu.scenes]: must save tiles before scenes. ==> run.setup.tiles'


#
# WORKER SETUP
#
MODULES=[
    'config',
    'utils',
    'ulu.scenes',
    'dl_jobs'
]



#
# PUBLIC
#
def task(product,region=ALL,**kwargs):
    """ save scenes """
    force=dh.truthy(kwargs.get('force',False))
    noisy=dh.truthy(kwargs.get('noisy',True))
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
def _scenes_job(product,region,force,noisy,limit):
    tiles_path=info.get_tiles_path(product,region,limit)
    if not os.path.isfile(tiles_path):
        raise ValueError( TILES_REQUIRED.format(tiles_path) )
    else:
        path=info.get_scenes_path(tiles_path,product)
        if os.path.isfile(path):
            if force:
                os.remove(path) 
            else:
                raise ValueError( SCENES_EXIST.format(path) )
        tile_keys=h.read_pickle(tiles_path)
        kwargs=info.get_scenes_kwargs(product,region,limit)
        args_list=dh.update_list(kwargs,tile_keys,'tile_key')
        job=DLJob(
            module_name='ulu.scenes',
            method_name='save_scenes',
            args_list=args_list,
            save_results=path,
            modules=MODULES,
            cpu_job=True,
            gpus=None,
            platform_job=True,
            noisy=noisy )
        return job

