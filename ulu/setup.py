from __future__ import print_function
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from dl_jobs.decorators import as_json, expand_args, attempt
import utils.helpers as h
import utils.dlabs as dlabs
import utils.load as load
from config import TILES_DIR
#
# CONSTANTS
#
TILES_EXIST='ERROR[ulu.save_tiles]: tile_set ({}) exists. use force=True to overwrite'


def get_tiles_path(product,region):
    meta=load.meta(product)
    run_cfig=meta['run']
    tile_set=run_cfig.get('tile_set')   
    if tile_set:
        path='{}/{}'.format(TILES_DIR,tile_set)
    else:
        res,size,pad=h.resolution_size_padding(meta=meta)
        version=run_cfig.get('version')   
        path=h.tile_keys_path( region,res,size,pad,version )
    return path



@as_json
@attempt
@expand_args
def save_tiles(product,region,limit=None,force=False):
    path=get_tiles_path(product,region)
    if force or (not os.path.isfile(path)):
        tile_keys=dlabs.get_tile_keys(product,region)
        h.save_pickle(tile_keys,path)
        return { 
            'action': 'save_tiles',
            'path': path ,
            'count': len(tile_keys) }
    else:
        raise ValueError( TILES_EXIST.format(path) )

