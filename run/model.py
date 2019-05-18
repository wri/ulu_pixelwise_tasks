from __future__ import print_function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from dl_jobs.job import DLJob
import utils.helpers as h
import ulu.info as info
from config import CONFIRM_DELETE

#
# CREATION TASKS
#
def upload(product,**kwargs):
    job_kwargs=info.get_model_kwargs(product)
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