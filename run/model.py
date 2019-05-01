from __future__ import print_function
from dl_jobs.job import DLJob
import utils.helpers as h
import ulu.info as info
from config import CONFIRM_DELETE



#
# CREATION TASKS
#
UPLOAD_KWARGS=[
    'key',
    'filename',
    'model_path',
    'models_root',
    'dls_root'
]
def upload(*args,**kwargs):
    model_cfig=info.get_model_config(args[0])
    job_kwargs=h.extract_kwargs(model_cfig,UPLOAD_KWARGS,required=False)
    job=DLJob(
        module_name='ulu.model',
        method_name='upload',
        kwargs=job_kwargs,
        platform_job=False,
        noisy=kwargs.get('noisy',True),
        log=False )
    return job



#
# DELETION TASKS
#
DELETE_KWARGS=[
    'key',
    'dls_root'
]
def delete(*args,**kwargs):
    model_cfig=info.get_model_config(args[0])
    job_kwargs=h.extract_kwargs(model_cfig,DELETE_KWARGS,required=False)
    confirm=kwargs.get('confirm')
    if h.truthy(confirm):
        job=DLJob(
            module_name='ulu.model',
            method_name='delete',
            kwargs=job_kwargs,
            platform_job=False,
            noisy=kwargs.get('noisy',True),
            log=False )
        return job
    else:
        print(CONFIRM_DELETE)
        job=None
    return job