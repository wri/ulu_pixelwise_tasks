from __future__ import print_function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from dl_jobs.job import DLJob
import utils.helpers as h
import ulu.info as info
from config import CONFIRM_DELETE
import dl_jobs.helpers as dh
#
# CONSTANTS
#
DLS_ROOT='modules/dev'
#
# DL FUNCTION ARGS
#
MODULES=[
    'aot',
    'ulu.aot'
]
REQUIREMENTS=[
    'numba==0.43.1'
]
#
# CREATION TASKS
#
def window_cloud_scores(**kwargs):
    job=DLJob(
        module_name='ulu.aot',
        method_name='window_cloud_scores',
        args=[kwargs.get('dls_root',DLS_ROOT)],
        platform_job=True,
        modules=MODULES,
        requirements=REQUIREMENTS,
        cpu_job=kwargs.get('cpu',True),
        noisy=kwargs.get('noisy',True),
        log=False )
    return job