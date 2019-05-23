import json
import geojson
import geopandas as gpd
from rasterio.crs import CRS
import requests as req


DEFAULT_COUNTRY='india'
LOCAL_CRS=32644
LOCAL_SRS=f"EPSG:{LOCAL_CRS}"
GLOBAL_CRS=4236
PIXEL_DELTA=416
RESOLUTION=1

#
# GEOJSON/GEOPANDAS HELPERS
#
def fetch_epsg(city=None,country=DEFAULT_COUNTRY,noisy=True):
    if city:
        q=f'{city}+{country}'
    else:
        q=country
    r=req.get(REQ_TMPL.format(q))
    jsn=r.json()[0]
    lat,lon=float(jsn['lat']),float(jsn['lon'])
    epsg=get_epsg(lat,lon)
    if noisy:
        print(q,epsg)
    return epsg


def get_epsg(lat,lon):
    return 32700-round((45+lat)/90)*100+round((183+lon)/6)


def get_crs(crs,as_dict=False):
    if isinstance(crs,int):
        crs_dict={'init':f'epsg:{crs}'}
    elif isinstance(crs,str):
        crs_dict={'init':crs}
    else:
        return crs
    if as_dict:
        return crs_dict
    else:
        return CRS(crs_dict)


def crs_res_bounds(profile):
    """ get crs, resolution and bounds form image profile """
    affine=profile['transform']
    res=affine.a
    minx=affine.c
    miny=affine.f-profile['height']*res
    maxx=minx+profile['width']*res
    maxy=miny+profile['height']*res
    crs=str(profile['crs'])
    return crs,res,(minx,miny,maxx,maxy)


def buffer_bounds(
        bounds=None,
        xmin=None,
        ymin=None,
        xmax=None,
        ymax=None,
        delta=None):
    if bounds:
        xmin,ymin,xmax,ymax=bounds
    if delta:
        xmin,ymin,xmax,ymax=xmin-delta,ymin-delta,xmax+delta,ymax+delta
    return xmin,ymin,xmax,ymax


def bounds_geometry(
        bounds=None,
        xmin=None,
        ymin=None,
        xmax=None,
        ymax=None,
        delta=None,
        as_feat=False,
        as_fc=False,
        as_gdf=False,
        crs=None,
        props={}):
    xmin,ymin,xmax,ymax=buffer_bounds(bounds,xmin,ymin,xmax,ymax,delta)
    coords=[[
        [xmin,ymax],
        [xmax,ymax],
        [xmax,ymin],
        [xmin,ymin],
        [xmin,ymax]]]
    geom={"coordinates": coords, "type": "Polygon"}
    if as_feat or as_fc or as_gdf:
        geom={'geometry':geom,'type':'Feature'}
        if props:
            geom['properties']=props
    if as_fc or as_gdf:
        geom={'features':[geom],'type':'FeatureCollection'}
    geom=geojson.loads(json.dumps(geom))
    if as_gdf:
        geom=gpd.GeoDataFrame.from_features(geom,crs=get_crs(crs))
    return geom


def gdf_to_geojson(gdf,crs=None):
    if crs:
        gdf.to_crs(CRS({'init': f'epsg:{crs}'}))
    return geojson.loads(gdf.geometry.to_json())


def gdf_bounds(gdf):
    gjsn=gdf_to_geojson(gdf)
    return gjsn['bbox']


def global_local_buffered_bounds(
        bounds,
        local_crs=LOCAL_CRS,
        pixel_delta=PIXEL_DELTA,
        resolution=RESOLUTION):
    delta=pixel_delta*resolution
    gdf=geometry_to_gdf(bounds=bounds)
    gdf.crs=get_crs(GLOBAL_CRS)
    gdf_local=gdf.to_crs(get_crs(local_crs))
    local_bounds=list(gdf_local.bounds.iloc[0])
    local_bounds_buffered=buffer_bounds(bounds=local_bounds,delta=delta)
    gdf_local_buffered=geometry_to_gdf(bounds=local_bounds_buffered)
    gdf_local_buffered.crs=get_crs(LOCAL_CRS)
    gdf_buffered=gdf_local_buffered.to_crs(get_crs(GLOBAL_CRS))
    bounds_buffered=list(gdf_buffered.bounds.iloc[0])
    return bounds_buffered, local_bounds_buffered


def write_geojson(output,path,pretty=False):
    if isinstance(output,str):
        output=geojson.loads(output)
    with open(path, "w") as file:
        if pretty:
            geojson.dump(output, file, indent=4, sort_keys=True)
        else:
            geojson.dump(output, file)




