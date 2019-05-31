from __future__ import print_function
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from dl_jobs.decorators import as_json, expand_args, attempt
import utils.dlabs as dlabs
#
# JOBS
#
@as_json
@attempt
@expand_args
def save_tiles(path,product,region,limit=None):
    tile_keys,meta=dlabs.get_tile_keys(
        path=path,
        product=product,
        region=region,
        limit=limit,
        return_info=True)
    meta['action']='save_tiles'
    return meta





