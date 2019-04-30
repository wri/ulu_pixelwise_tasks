from __future__ import print_function
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
    'dl_jobs'
]
REQUIREMENTS=[
    'descarteslabs[complete]>=0.18',
    'numpy==1.16.3',
    'rasterio==1.0.22',
    'requests==2.21.0',
    'matplotlib==2.2.3',
    'keras==2.1.2',
    'tensorflow==1.1.0'
]
GPUS=1



#
# TASKS
#
def task(*args,**kwargs):
    product=args[0]
    limit=kwargs.get('limit',None)
    date_index=kwargs.get('date',None)
    region_index=kwargs.get('region',None)
    args_list=info.config_list(
        product,
        date_index=date_index,
        region_index=region_index)
    if limit:
        args_list=args_list[:int(limit)]
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



