from __future__ import print_function
from dl_jobs.job import DLJob
from utils.helpers import truthy
import ulu.info as info

CONFIRM_DELETE="ULU.product.delete: pass 'confirm=True' to delete product"
#
# TASKS
#
def delete(*args,**kwargs):
    job_kwargs=info.get_config(args[0])
    confirm=kwargs.get('confirm')
    if truthy(confirm):
        job=DLJob(
            module_name='ulu.product',
            method_name='delete',
            kwargs=job_kwargs,
            platform_job=False,
            noisy=kwargs.get('noisy',True),
            log=False )
    else:
        print(CONFIRM_DELETE)
        job=None
    return job



def create(*args,**kwargs):
    job_kwargs=info.get_config(args[0])
    job=DLJob(
        module_name='ulu.product',
        method_name='create',
        kwargs=job_kwargs,
        platform_job=False,
        noisy=kwargs.get('noisy',True),
        log=False )
    return job


def add_bands():
    pass


def add_band():
    pass



