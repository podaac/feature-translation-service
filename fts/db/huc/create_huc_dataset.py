#!/usr/bin/env python
# flake8: noqa
# pylint: disable=unused-variable

"""
==============
create_huc_dataset.py
==============

Set of primary functions used create the HUC portion of the Feature Translation
   Service. Takes in command line input, and aggregates input USGS data into a
   single, consolidated database of simplified polygons and bounding boxes.
"""
import argparse
import os
import sys

import geopandas as gpd
import pandas as pd

from fts.db.huc.remove_multipolygons import remove
from fts.db.huc.simplify_huc import create_resolutions_and_combine


def combine(arguments):
    """
    Create final database including simplified polygons and HUCs.

    Parameters
    ----------
    arguments : dict
        Dictionary of parsed command line arguments

    Returns
    -------
    None
    """

    # Read in command line arguments
    in_dir = arguments['i']
    out_dir = arguments['o']
    vertices = arguments['v']

    if not in_dir.endswith("/"):
        in_dir += "/"
    if not out_dir.endswith("/"):
        out_dir += "/"

    huc_list = []
    for root, dirs, files in os.walk(in_dir):
        for file in files:
            if file.endswith(".shp") and file.startswith("WBDHU"):
                huc_list.append(os.path.join(root, file))

    if not huc_list:
        print("No shapefiles found. Make sure you have a directory of HUC subfolders in place.")
        sys.exit(1)

    # Create local directory at 'output directory' location if it doesn't already
    # exist
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    print("\nCreating HUC dataset... ")
    final_df = parse_huc(huc_list)
    final_df['Geo_Without_Multipolygons'] = final_df.apply(lambda row:
                                                           remove(row['Geometry']), axis=1)

    # Function in 'simplify_HUC.py'
    create_resolutions_and_combine(final_df, out_dir, vertices)


def parse_huc(huc_list):
    """
    Creates single, consolidated HUC database without simplified polygons.
       Ready for simplification process next.

    Parameters
    ----------
    huc_list : list
        List of HUC files

    Returns
    -------
    pandas.core.frame.DataFrame: DataFrame consisting of the data found in the the HUC files
    """

    final_df = pd.DataFrame()
    for element in huc_list:
        temp_df = gpd.read_file(element)
        # Extract HUC level for indexing (2, 4, 6, 8, ...)
        try:
            huc_category = int(element.split('.')[-2][-2:])
        except ValueError:
            huc_category = int(element.split('.')[-2][-1:])

        temp_df = temp_df[['huc{}'.format(huc_category), 'name', 'geometry']]
        temp_df.columns = ['HUC', 'Region', 'Geometry']
        temp_df['HUC'] = temp_df['HUC'].astype(str)

        # Concatenate each shapefile DataFrame together
        final_df = pd.concat([final_df, temp_df])

    return final_df


def parse_huc_arguments():
    """
    Parse HUC arguments. Input, output, AND polygon information required

    Returns
    -------
    dict: dictionary of parsed command line arguments
    """

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group('required arguments')
    required.add_argument('-i', help='input directory', required=True)
    required.add_argument('-o', help='output directory', required=True)
    required.add_argument('-v', help='max vertices of polygons', required=True)
    args = parser.parse_args()
    args = vars(args)

    return args


if __name__ == "__main__":
    ARGS = parse_huc_arguments()
    combine(ARGS)
