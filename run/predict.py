from __future__ import print_function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from dl_jobs.job import DLJob
import ulu.info as info


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
def task(*args,**kwargs):
    product=args[0]
    nb_scenes=kwargs.get('nb_scenes',False)
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
    if hard_limit:
        args_list=args_list[:hard_limit]
    job=DLJob(
        module_name='ulu.prediction',
        method_name='predict',
        args_list=args_list,
        modules=MODULES,
        requirements=REQUIREMENTS,
        data=DATA,
        gpus=GPUS,
        platform_job=True,
        dl_image=kwargs.get('dl_image'),
        noisy=kwargs.get('noisy'),
        log=False )
    return job





