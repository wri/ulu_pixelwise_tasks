from __future__ import print_function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from dl_jobs.job import DLJob
import dl_jobs.helpers as dh
from utils.helpers import truthy
import ulu.info as info
from config import CONFIRM_DELETE

#
# CREATION TASKS
#
def create(product,**kwargs):
    job_kwargs=info.get_product_kwargs(product)
    job=DLJob(
        module_name='ulu.product',
        method_name='create',
        kwargs=job_kwargs,
        platform_job=False,
        noisy=kwargs.get('noisy',True))
    return job


def add_bands(product,**kwargs):
    band_configs=info.get_bands_kwargs_list(product)
    job=DLJob(
        module_name='ulu.product',
        method_name='add_bands',
        args=band_configs,
        platform_job=False,
        noisy=kwargs.get('noisy',True))
    return job


def add_band(product,band_index,**kwargs):
    band_configs=info.get_bands_kwargs_list(product)
    band_index=int(band_index)
    job=DLJob(
        module_name='ulu.product',
        method_name='add_band',
        kwargs=band_configs[band_index],
        platform_job=False,
        noisy=kwargs.get('noisy',True))
    return job


#
# DELETION TASKS
#
def delete(product,**kwargs):
    job_kwargs=info.get_delete_product_kwargs(
        product,
        kwargs.get('cascade',True))
    confirm=kwargs.get('confirm')
    if truthy(confirm):
        job=DLJob(
            module_name='ulu.product',
            method_name='delete',
            kwargs=job_kwargs,
            platform_job=False,
            noisy=kwargs.get('noisy',True),)
        return job
    else:
        print(CONFIRM_DELETE)


def remove_bands(product,**kwargs):
    band_configs=info.get_bands_kwargs_list(product)
    confirm=kwargs.get('confirm')
    if truthy(confirm):
        job=DLJob(
            module_name='ulu.product',
            method_name='remove_bands',
            args=band_configs,
            platform_job=False,
            noisy=kwargs.get('noisy',True),)
        return job
    else:
        print(CONFIRM_DELETE)


def remove_band(product,band_index,**kwargs):
    band_configs=info.get_bands_kwargs_list(product)
    band_index=int(band_index)
    confirm=kwargs.get('confirm')
    if truthy(confirm):
        job=DLJob(
            module_name='ulu.product',
            method_name='remove_band',
            kwargs=band_configs[band_index],
            platform_job=False,
            noisy=kwargs.get('noisy',True),)
        return job
    else:
        print(CONFIRM_DELETE)

