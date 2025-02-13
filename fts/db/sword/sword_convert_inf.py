#! /usr/bin/env python

"""
Converts inf values to NaN in SWORD shapefiles
"""
import os
import glob
import numpy as np
import geopandas as gpd

# recursively get shapefiles
SWORD_SHPFILES = '/shp/*/*.shp'
SWORD_SHPFILES = '/Users/tebaldi/Desktop/shp/*/*.shp'

for filepath in glob.iglob(SWORD_SHPFILES, recursive=True):
    print(filepath)

    df = gpd.read_file(filepath)

    INF_FOUND = False

    # check each column that could contain inf values
    for col_name in df.select_dtypes(exclude=[object, 'geometry']):
        if np.isinf(df[col_name]).any():
            print('column ' + col_name + ' contains inf value')
            INF_FOUND = True
            df[col_name].replace([np.inf, -np.inf], np.nan, inplace=True)

    # overwrite the corrected file in place
    if INF_FOUND:
        print('writing corrected file to ' + filepath)
        df.to_file(filename=filepath)
