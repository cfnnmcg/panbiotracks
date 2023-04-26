#!/usr/bin/env python3

import argparse
import sys
import os
import geopandas as gp
import pandas as pd
import itertools as itt
from shapely.geometry import Point

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

from modules.algorithms import nodes_intersect as ni
from modules import coords_list

parser = argparse.ArgumentParser(description='Input and output files.')
parser.add_argument('-i', '--input',
                    dest='gt_shp_list',
                    nargs='+',
                    help='List of generalized tracks. Needs at least 2.')
parser.add_argument('-o', '--output',
                    dest='shp_file',
                    help="Location and name of the output file, "
                    "without file extension.")
args = parser.parse_args()

gt_gp_list = []

for i in args.gt_shp_list:
    k = gp.read_file(i)
    gt_gp_list.append(k)

for a, b in itt.combinations(gt_gp_list, 2):
    nodes_list = ni(a, b)
    if len(nodes_list[~nodes_list.is_empty]) == 0:
        continue
    else:
        nodes_coord_list = list(zip(nodes_list.geometry.x.astype(float),
            nodes_list.geometry.y.astype(float)))
        coords_list = [*coords_list, *nodes_coord_list]

coords_list_df = pd.DataFrame(coords_list, columns=['lon', 'lat'])
#coords_list_df = coords_list_df[['lat', 'lon']]

coords_list_df['geometry'] = (coords_list_df.apply
                                (lambda x: Point(x.lon, x.lat), axis=1))
coords_list_df = coords_list_df.drop(['lon', 'lat'], axis=1)
coords_list_gdf = gp.GeoDataFrame(coords_list_df)

coords_list_gdf.to_file(args.shp_file)

#Buscar intersección
# def find_nodes(t1, t2, filename):
#     inter = t1.intersection(t2)
#     inter.to_file(filename)

# find_nodes(l1, l2, "./outputs/nodes_t1-t2")
