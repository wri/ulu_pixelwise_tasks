from dl_jobs.decorators import as_json, expand_args
import utils.load as load
import utils.dlabs as dlabs




#
# PRODUCT META
#
# def config(product,date_index=None,region_index=None):
#     meta=load.meta(product)
#     run_cfig=meta['run']
#     product_cfig=meta['product']
#     input_cfig=meta['input']
#     dates=h.extract_list(run_cfig['dates'],date_index)
#     regions=h.extract_list(run_cfig['regions'],region_index)
#     product_bands=product_cfig['bands']
#     return {
#             'product': product_cfig['name'],
#             'model': model_name(**['model']),
#             'model_filename': run_cfig['model'].get('filename'),
#             'model_key': run_cfig['model'].get('key'),
#             'window': run_cfig['window'],
#             'pad': get_padding(run_cfig['pad'],run_cfig['window'])
#             'water_mask': 'water_mask' in product_bands,
#             'cloud_mask': 'cloud_mask' in product_bands
#             'input_products': input_cfig['products'],
#             'input_bands': input_cfig['bands']
#         }



# @as_json
# @expand_args
# def tiles(product):
#     regions=load.meta(product,'run','regions')
#     out=[]
#     for region in regions:
#         _,info=dlabs.get_tile_keys(
#             region=region,
#             product=product,
#             return_info=True)
#         out.append(info)
#     return out