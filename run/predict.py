from __future__ import print_function
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from dl_jobs.job import DLJob
import dl_jobs.nd_json as ndj
import utils.helpers as h
import utils.load as load
import ulu.info as info
#
# CONSTANTS
#
ALL='all'
SCENES_REQUIRED='ERROR[ulu.predict]: must save scenes before predicting. ==> run.setup.scenes'


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
REQUIREMENTS=[]
GPUS=1


#
# TASKS
#
def task(product,region=ALL,**kwargs):
    force=h.truthy(kwargs.get('force',False))
    noisy=h.truthy(kwargs.get('noisy',True))
    limit=kwargs.get('limit',False)
    if region==ALL:
        regions=load.meta(product,'run','regions')
        jobs=[]
        for region in regions:
            jobs.append(_predict_job(product,region,force,noisy,limit))
        return jobs
    else:
        return _predict_job(product,region,force,noisy,limit)



def _predict_job(product,region,force,noisy,limit):
    tiles_path=info.get_tiles_path(product,region,limit)
    scenes_path=info.get_scenes_path(tiles_path,product)
    results_path, add_timestamp=info.get_prediction_path(tiles_path,product)
    if not os.path.isfile(scenes_path):
        raise ValueError( SCENES_REQUIRED.format(scenes_path) )
    scenes_args_list=ndj.read(scenes_path)
    kwargs=info.get_predict_kwargs(product,region,limit)
    args_list=h.update_list(kwargs,scenes_args_list)
    job=DLJob(
        module_name='ulu.predict',
        method_name='predict',
        args_list=args_list,
        save_results=results_path,
        results_timestamp=add_timestamp,
        modules=MODULES,
        cpu_job=False,
        gpus=GPUS,
        platform_job=True,
        noisy=noisy )
    return job





