#!/usr/bin/env python3

import sys
import os
import argparse
import pandas as pd
import geopandas as gp
import numpy as np
import itertools as itt
from vincenty import vincenty_inverse as vc
from shapely.geometry import Point

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

from modules.functions import (
    add_vertex, add_edge, prim_algorithm as prim, shp_writer as shpw,
    nodes_intersect as ni)
from modules import graph, edge_list, edges, coords_list

# Define script arguments
parser = argparse.ArgumentParser(description='Options, input, output files.')
parser.add_argument('-m', '--mode',
                    choices=['I', 'P', 'N'],
                    help="Select the operation mode: 'I' generates individual "
                    "tracks. 'P' generates pseudo-generalized tracks. "
                    "'N' generates nodes.")
parser.add_argument('-i', '--input',
                    nargs='+',
                    # dest='csv_file',
                    # action='append',
                    help="Input file or files. "
                    "If '-m I', it needs to be a single CSV file "
                    "with only two columns: lat (Latitude) and "
                    "lon (Longitude), in that explicit order.\n"
                    "If '-m P' or '-m N', it must be a list of at least two "
                    "SHP files.")
parser.add_argument('-o', '--output',
                    dest='shp_file', 
                    help="Location and name of the SHP output "
                    "file, without extension.")
args = parser.parse_args()

if args.mode == 'I':
    # Individual Tracks method
    # Opening CSV file and deleting duplicate records
    for i in args.input:
        with open(i) as fo:
            df = pd.read_csv(fo, header=0, dtype={'lat': float, 'lon': float})
            df.drop_duplicates(inplace=True)

        # Adding vertices
        for r in range(df.shape[0]):
            add_vertex(r)

        # Adding edges and their weight (lenght)
        df_list = df.values.tolist()
        for i in range(len(df_list)):
            for j in range(len(df_list)):
                la = tuple(df_list[i])
                lo = tuple(df_list[j])
                add_edge(i, j, vc(la, lo))

        # Prim function to calculate MST
        print("\nMinimal distances:")
        prim(df.shape[0], graph, edges)

        # Making tuples of points to trace edges.
        coords = df.to_numpy()
        edges = np.array(edges, dtype=np.int32)
        for e in edges:
            i, j = e
            edge_list.append([(coords[i, 1], coords[i, 0]),
            (coords[j, 1], coords[j, 0])])
        edge_list = list(sorted(edge_list))

        # Saving the MST to a SHP file
        shpw(args.shp_file)
elif args.mode == 'P':
    # Pseudo-Generalized Tracks method
    # Global list of input files' paths
    gp_it_list = []
    for i in args.input:
        k = gp.read_file(i)
        gp_it_list.append(k)

    # Making intersections
    for a, b in itt.combinations(gp_it_list, 2): # type: ignore
        nodes_list = ni(a, b)
        if len(nodes_list[~nodes_list.is_empty]) == 0:
            continue
        else:
            nodes_coord_list = list(zip(nodes_list.geometry.x.astype(float),
                nodes_list.geometry.y.astype(float)))
            coords_list = [*coords_list, *nodes_coord_list]

    # Making dataframe
    coords_list_df = pd.DataFrame(coords_list, columns=['lon', 'lat'])
    coords_list_df = coords_list_df[['lat', 'lon']]

    # Adding vertices
    for r in range(coords_list_df.shape[0]):
        add_vertex(r)

    # Adding edges and their weight (lenght)
    df_list = coords_list_df.values.tolist()
    for i in range(len(df_list)):
        for j in range(len(df_list)):
            la = tuple(df_list[i])
            lo = tuple(df_list[j])
            add_edge(i, j, vc(la, lo))

    # Prim function to calculate MST
    print("\nDistancias mínimas:")
    prim(coords_list_df.shape[0], graph, edges)

    # Making tuples of points to trace edges.
    coords = coords_list_df.to_numpy()
    edges = np.array(edges, dtype=np.int32)
    for e in edges:
        i, j = e
        edge_list.append([(coords[i, 1], coords[i, 0]),
        (coords[j, 1], coords[j, 0])])
    edge_list = list(sorted(edge_list))

    # Saving the MST shapefile
    shpw(args.shp_file)
elif args.mode == 'N':
    # Nodes method
    # Global list of generalized tracks
    gt_gp_list = []
    for i in args.input:
        k = gp.read_file(i)
        gt_gp_list.append(k)

    # Finding intersections
    for a, b in itt.combinations(gt_gp_list, 2): # type: ignore
        nodes_list = ni(a, b)
        print(nodes_list)
        if len(nodes_list[~nodes_list.is_empty]) == 0:
            continue
        else:
            nodes_coord_list = list(zip(nodes_list.geometry.x.astype(float),
                nodes_list.geometry.y.astype(float)))
            coords_list = [*coords_list, *nodes_coord_list]

    print(coords_list)

    # Making list of coordinates
    coords_list_df = pd.DataFrame(coords_list, columns=['lon', 'lat'])
    coords_list_df['geometry'] = (coords_list_df.apply
                                    (lambda x: Point(x.lon, x.lat), axis=1))
    coords_list_df = coords_list_df.drop(['lon', 'lat'], axis=1)

    # Saving SHP output file
    coords_list_gdf = gp.GeoDataFrame(coords_list_df)
    coords_list_gdf.to_file(args.shp_file, driver='ESRI Shapefile') # type: ignore
else:
    print(f"{args.mode} is not a valid option. Please use 'I', 'P' or 'N'.")