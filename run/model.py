from __future__ import print_function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from dl_jobs.job import DLJob
import utils.helpers as h
import ulu.info as info
from config import CONFIRM_DELETE
import dl_jobs.helpers as dh
#
# CREATION TASKS
#
def upload(product,**kwargs):
    model=kwargs.get('model')
    key=kwargs.get('key')
    filename=kwargs.get('filename')
    job_kwargs=info.get_model_kwargs(product,model,key,filename)
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
def delete(product,**kwargs):
    job_kwargs=info.get_model_kwargs(product)
    confirm=kwargs.get('confirm')
    if dh.truthy(confirm):
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