# !/usr/bin/python
# flake8: noqa

"""
Group of functions that performs the simplification algorithms, converts the
   results to a CMR queryable string, and writes individual HUCs to shapefiles
"""
import os
import re
import shutil
import time
import warnings
import zipfile

import geopandas as gpd
import numpy as np
import shapely
import visvalingamwyatt as vw
from shapely.geometry import Polygon
from tqdm import tqdm

warnings.filterwarnings('ignore')


def format_polygon(polygon):
    """
    Function that takes a polygon as input and returns a string formatted to
       be queryable through CMR

    Parameters
    ----------
    polygon

    Returns
    -------

    """
    # Re-orient polygon points to be counter-clockwise and in the correct
    # CMR format
    polygon = shapely.geometry.polygon.orient(polygon, sign=1.0)
    coords = str(list(polygon.exterior.coords))
    cmr_polygon = re.sub(r'[()[\]\s+]', '', coords)

    return cmr_polygon


def write_to_shapefiles(multi_geometry, huc, shapefile_location):
    """
    Write all unsimplified geometries to shapefile with name as HUC

    Parameters
    ----------
    multi_geometry
    huc
    shapefile_location

    Returns
    -------

    """
    base_path = huc + "/" + huc
    try:
        # Convert to GeoSeries to be able to convert geometry to shapefile
        geometry = gpd.GeoSeries(multi_geometry)
        os.mkdir(shapefile_location + huc)  # Make a directory with name = HUC
        geometry.to_file(shapefile_location + '{}.shp'.format(base_path))
    except FileExistsError as err:
        print(err)
        time.sleep(0.1)  # Race condition may occur with Pandas apply
        geometry = gpd.GeoSeries(multi_geometry)
        geometry.to_file(shapefile_location + '{}.shp'.format(base_path))

    # Just used to create the ZIP files to upload to S3
    with zipfile.ZipFile('{}.zip'.format(shapefile_location + huc), 'w') as zipf:
        zipf.write(shapefile_location + '{}.shp'.format(base_path),
                   arcname='{}'.format(huc + "/") + huc + ".shp")
        zipf.write(shapefile_location + '{}.cpg'.format(base_path),
                   arcname='{}'.format(huc + "/") + huc + ".cpg")
        zipf.write(shapefile_location + '{}.shx'.format(base_path),
                   arcname='{}'.format(huc + "/") + huc + ".shx")
        zipf.write(shapefile_location + '{}.dbf'.format(base_path),
                   arcname='{}'.format(huc + "/") + huc + ".dbf")

    shutil.rmtree(shapefile_location + huc)


def simplify(multi_geometry, single_geometry, length, max_vertices):
    """
    Function that takes in a polygon and returns a simplified version taking
    the convex hull of the region.

    Parameters
    ----------
    multi_geometry
    single_geometry
    length
    max_vertices

    Returns
    -------

    """
    # Convert to GeoPandas Series and perform convex hull operation
    polygons = gpd.GeoSeries(multi_geometry)
    polygons_hull = polygons.convex_hull.item()

    # Format into CMR queryable polygon
    complex_hull_cmr_poly = format_polygon(polygons_hull)

    #######################

    # Map the reduction of vertices to a tanh function
    reduction = int(max_vertices * np.tanh((1 / max_vertices) * length))

    # Initial simplification
    points = list(single_geometry.exterior.coords)
    simplifier = vw.Simplifier(points)

    visval_poly_points = simplifier.simplify(number=reduction)
    visval_poly = Polygon(visval_poly_points)
    visval_cmr_poly = format_polygon(visval_poly)

    ######################

    bbox = str(polygons_hull.bounds)
    cmr_bbox = re.sub(r'[()\s+]', '', bbox)

    return complex_hull_cmr_poly, visval_cmr_poly, cmr_bbox


def create_resolutions_and_combine(full_df, out_dir, max_vertices):
    """
    Function used to call helper functions above. Writes output database to
       HUC_Data.csv file.
    Parameters
    ----------
    full_df
    out_dir
    max_vertices

    Returns
    -------

    """
    # Used to display progress bar
    tqdm.pandas()

    shapefile_location = "Shapefiles/"
    if os.path.exists(out_dir + shapefile_location):
        shutil.rmtree(out_dir + shapefile_location)

    os.mkdir(out_dir + shapefile_location)

    full_df['len'] = full_df.apply(lambda row:
                                   len(list(row['Geo_Without_Multipolygons'].exterior.coords)),
                                   axis=1)

    # full_df = full_df.loc[full_df.index < 200]

    print("Writing to shapefiles...")
    full_df.progress_apply(lambda row: write_to_shapefiles(row['Geometry'], row['HUC'],
                                                           out_dir + shapefile_location), axis=1)

    # Iterate over all rows in dataframe and simplify
    print("Simplifying polygons...")
    full_df['Polygon Convex Hull'], \
    full_df['Polygon Visvalingam'], \
    full_df['Bounding Box'] = zip(*full_df.progress_apply(lambda row:
                                                          simplify(row['Geometry'],
                                                                   row['Geo_Without_Multipolygons'],
                                                                   row['len'],
                                                                   int(max_vertices)),
                                                          axis=1))

    full_df.drop(['Geo_Without_Multipolygons', 'len', 'Geometry'], inplace=True, axis=1)

    print("Writing to file.")
    full_df.to_csv(out_dir + 'HUC_Data.csv', index=False)
    print("Done!")
