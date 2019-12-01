from __future__ import print_function
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from dl_jobs.job import DLJob
import dl_jobs.nd_json as ndj
import utils.helpers as h
import utils.load as load
import ulu.info as info
import dl_jobs.helpers as dh
#
# CONSTANTS
#
ALL='all'
WARN_NO_SCENES='WARNING:\n\t- scene_set not found({})\n\t- running from tile_set'
CPU_JOB=True

#
# DL FUNCTION ARGS
#
DATA=None
MODULES=[
    'config',
    'utils',
    'ulu',
    'run',
    'mproc',
    'dl_jobs'
]
REQUIREMENTS=[
    'tensorflow==1.14.0',
    'numba==0.43.1'
]

GPUS=1
CPUS=2
TASK_KWARGS={ 'memory': '10Gi' }


#
# TASKS
#
def task(product,region=ALL,**kwargs):
    log=kwargs.get('log',True)
    force=dh.truthy(kwargs.get('force',False))
    noisy=dh.truthy(kwargs.get('noisy',True))
    cpu_job=dh.truthy(kwargs.get('cpu',CPU_JOB))
    gpus=kwargs.get('gpus',GPUS)
    if gpus: gpus=int(gpus)
    limit=kwargs.get('limit',False)
    if region==ALL:
        regions=load.meta(product,'run','regions')
        jobs=[]
        for region in regions:
            jobs.append(_predict_job(log,product,region,force,noisy,limit,cpu_job,gpus))
        return jobs
    else:
        return _predict_job(log,product,region,force,noisy,limit,cpu_job,gpus)



def _predict_job(log,product,region,force,noisy,limit,cpu_job,gpus):
    tiles_path=info.get_tiles_path(product,region,limit)
    scenes_path=info.get_scenes_path(tiles_path,product)
    if scenes_path and os.path.isfile(scenes_path):
        args_list=ndj.read(scenes_path)
    else:
        print(WARN_NO_SCENES.format(scenes_path))
        scenes_kwargs=info.get_scenes_kwargs(product,region,limit)
        tile_keys=h.read_pickle(tiles_path)
        args_list=dh.update_list(scenes_kwargs,tile_keys,'tile_key')
    results_path, add_timestamp=info.get_prediction_path(tiles_path,product)
    kwargs=info.get_predict_kwargs(product,region,limit)
    args_list=dh.update_list(kwargs,args_list)
    job=DLJob(
        module_name='ulu.predict',
        method_name='predict',
        args_list=args_list,
        save_results=info.path_root(results_path),
        results_timestamp=add_timestamp,
        modules=MODULES,
        requirements=REQUIREMENTS,
        task_kwargs=TASK_KWARGS,
        cpu_job=cpu_job,
        cpus=CPUS,
        gpus=gpus,
        log=log,
        platform_job=True,
        noisy=noisy )
    return job





