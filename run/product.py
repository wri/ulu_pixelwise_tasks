from __future__ import print_function
from dl_jobs.job import DLJob
from utils.helpers import truthy
import ulu.info as info
from config import CONFIRM_DELETE



#
# CREATION TASKS
#
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


def add_bands(*args,**kwargs):
    band_configs=info.get_bands_config(args[0])
    job=DLJob(
        module_name='ulu.product',
        method_name='add_bands',
        args=band_configs,
        platform_job=False,
        noisy=kwargs.get('noisy',True),
        log=False )
    return job


def add_band(*args,**kwargs):
    band_configs=info.get_bands_config(args[0])
    band_index=int(args[1])
    job=DLJob(
        module_name='ulu.product',
        method_name='add_band',
        kwargs=band_configs[band_index],
        platform_job=False,
        noisy=kwargs.get('noisy',True),
        log=False )
    return job


#
# DELETION TASKS
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


def remove_bands(*args,**kwargs):
    band_configs=info.get_bands_config(args[0])
    confirm=kwargs.get('confirm')
    if truthy(confirm):
        job=DLJob(
            module_name='ulu.product',
            method_name='remove_bands',
            args=band_configs,
            platform_job=False,
            noisy=kwargs.get('noisy',True),
            log=False )
    else:
        print(CONFIRM_DELETE)
        job=None
    return job


def remove_band(*args,**kwargs):
    band_configs=info.get_bands_config(args[0])
    band_index=int(args[1])
    confirm=kwargs.get('confirm')
    if truthy(confirm):
        job=DLJob(
            module_name='ulu.product',
            method_name='remove_band',
            kwargs=band_configs[band_index],
            platform_job=False,
            noisy=kwargs.get('noisy',True),
            log=False )
    else:
        print(CONFIRM_DELETE)
        job=None
    return job

