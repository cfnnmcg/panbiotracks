#!/usr/bin/env python3

# Panbiotracks v. 0.2.5
# (c) Carlos Fernando Castillo-García, Universidad Nacional Autónoma de México
# 2023-2025

# This program was made as a fulfillment of the author for obtaining a 
# M.Sc. degree in the Posgrado en Ciencias Biológicas, 
# Universidad Nacional Autónoma de México, Mexico. 
# The author thanks the Consejo Nacional de Humanidades, 
# Ciencias y Tecnologías (CONAHCyT) for the support of this research through 
# a graduate scholarship.

#import sys
#import os
import argparse
import glob
from pandas import read_csv as pdreadcsv, DataFrame as pddf
from geopandas import read_file as gprf, GeoDataFrame as gpgdf
#import numpy as np
from numpy import array as nparr, int32 as np32
#import itertools as itt
from itertools import combinations as itcomb
from vincenty import vincenty_inverse as vc
from shapely.geometry import Point
from pathlib import Path

#path = os.path.join(os.path.dirname(__file__), os.pardir)
#sys.path.append(path)

from modules.functions import (
    add_vertex, add_edge, prim_algorithm as prim, shp_writer as shpw,
    nodes_intersect as ni)
from modules import graph, edge_list, edges, coords_list, vertices

# Define script arguments
parser = argparse.ArgumentParser(prog = 'Panbiotracks',
                                 description='Panbiotracks - ' \
                                 'Options, and input and output files.')
parser.add_argument('-m', '--mode',
                    choices=['I', 'P', 'N'],
                    help="Select the operation mode: 'I' for individual "
                    "tracks. 'P' for internal generalized tracks. "
                    "'N' for generalized nodes.")
parser.add_argument('-i', '--input',
                    nargs='+',
                    help="Input file or files. "
                    "If '-m I', it must be a single CSV file "
                    "with three columns: species, lat (Latitude) and "
                    "lon (Longitude), in that order.\n"
                    "If '-m P' or '-m N', it must be a set of at least two "
                    "SHP files, separated by a space each. "
                    "It can also be a path with a wildcard (i.e. "
                    "/path/to/my/files/*.shp), in which case Panbiotracks will "
                    "process ALL of the SHP files within the given directory.")
parser.add_argument('-o', '--output',
                    dest='shp_file', 
                    help="If '-m I', it must be the path to the "
                    "directory where the SHP output files will be saved to. "
                    "If '-m P' or '-m N', it's the path and name of the "
                    "SHP output file, without file extension.")
parser.add_argument('-v', '--version',
                    action='version',
                    version='%(prog)s 0.2.5',
                    help="Displays the program's version and exits.")
args = parser.parse_args()

if args.mode == 'I':
    # INDIVIDUAL TRACKS METHOD
    # Opening CSV file and deleting duplicate records
    print(f"\n{len(args.input)} CSV file was loaded. "
          "Building Individual Tracks...")
    
    for i in args.input:
        with open(i) as fo:
            df = pdreadcsv(fo, header=0, dtype={'lat': float, 'lon': float})
            df.drop_duplicates(inplace=True)
            list_df = [g for n,g in df.groupby('species')]

        # Iterating over each dataframe:
        for dfi in list_df:

            # Clearing all lists:
            graph.clear()
            vertices.clear()
            edges.clear()
            edge_list.clear()
            coords_list.clear()

            # Adding vertices to the adjacency matrix:
            for r in range(dfi.shape[0]):
                add_vertex(r)

            # Adding edges and their weight (lenght) to the adjacency matrix:
            df_list = dfi[['lat', 'lon']].values.tolist()
            for i in range(len(df_list)):
                for j in range(len(df_list)):
                    la = tuple(df_list[i])
                    lo = tuple(df_list[j])
                    add_edge(i, j, vc(la, lo))

            # Prim function to calculate MST
            print(f"\n{dfi['species'].loc[dfi.index[0]]} - "
                f"Minimal distances between vertices:")
            prim(dfi.shape[0], graph, edges)

            # Making tuples of points to trace edges:
            coords = dfi.to_numpy()
            edges_np = nparr(edges, dtype=np32)
            for e in edges_np:
                i, j = e
                edge_list.append([(coords[i, 2], coords[i, 1]),
                (coords[j, 2], coords[j, 1])])

            # Saving the MST to a SHP file:
            filename = dfi['species'].loc[dfi.index[0]]
            shpw(f"{args.shp_file}/{filename}")
            print(f"The individual track was saved to "
                f"{args.shp_file}/{filename}.shp")
            print("\nEND")

elif args.mode == 'P':
    # INTERNAL GENERALIZED TRACKS METHOD
    # Global list of input files' paths
    gp_it_list = []
    
    # Check lenght of input to determine if there's a wildcard:
    if len(args.input) < 2:
        for item in args.input:
            if item.find('*') > -1:
                pre_it_list = glob.glob(args.input.pop(0))
                print(f"\n{len(pre_it_list)} SHP files were loaded. "
                      "Building Internal Generalized Track...")
                for i in pre_it_list:
                    k = gprf(i)
                    gp_it_list.append(k)
            else:
                print(f"\nERROR: Panbiotracks needs more than 1 input file "
                      "to perform this function. Add 2 or more files "
                      "after the '-i' flag and try again.")
                quit()
    else:
        print(f"\n{len(args.input)} SHP files were loaded. "
              "Building Internal Generalized Track...")
        for i in args.input:
            k = gprf(i)
            gp_it_list.append(k)

    # Making intersections
    for a, b in itcomb(gp_it_list, 2): # type: ignore
        nodes_list = ni(a, b)
        if len(nodes_list[~nodes_list.is_empty]) == 0:
            continue
        else:
            nodes_coord_list = list(zip(nodes_list.geometry.x.astype(float),
                nodes_list.geometry.y.astype(float)))
            coords_list = [*coords_list, *nodes_coord_list]

    # Making dataframe
    coords_list_df = pddf(coords_list, columns=['lon', 'lat'])
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
    print("\nMinimal distances between vertices:")
    prim(coords_list_df.shape[0], graph, edges)

    # Making tuples of points to trace edges.
    coords = coords_list_df.to_numpy()
    edges = nparr(edges, dtype=np32)
    for e in edges:
        i, j = e
        edge_list.append([(coords[i, 1], coords[i, 0]),
        (coords[j, 1], coords[j, 0])])
    edge_list = list(sorted(edge_list))

    # Saving the MST shapefile
    shpw(args.shp_file)
    print(f"\nThe internal generalized track was saved to {args.shp_file}.shp")
    print("\nEND")

elif args.mode == 'N':
    # NODES METHOD
    # Global list of generalized tracks
    gt_gp_list = []
    
    # Check lenght of input to determine if there's a wildcard:
    if len(args.input) < 2:
        for item in args.input:
            if item.find('*') > -1:
                pre_it_list = glob.glob(args.input.pop(0))
                print(f"\n{len(pre_it_list)} SHP files were loaded. "
                      "Finding Generalized Nodes...")
                for i in pre_it_list:
                    k = gprf(i)
                    gt_gp_list.append(k)
            else:
                print(f"\nERROR: Panbiotracks needs more than 1 input file "
                      "to perform this function. Add 2 or more files "
                      "after the '-i' flag and try again.")
                quit()
    else:
        print(f"\n{len(args.input)} SHP files were loaded. "
              "Finding Generalized Nodes...")
        for i in args.input:
            k = gprf(i)
            gt_gp_list.append(k)

    # Finding intersections
    for a, b in itcomb(gt_gp_list, 2): # type: ignore
        nodes_list = ni(a, b)
        if len(nodes_list[~nodes_list.is_empty]) == 0:
            continue
        else:
            nodes_coord_list = list(zip(nodes_list.geometry.x.astype(float),
                nodes_list.geometry.y.astype(float)))
            coords_list = [*coords_list, *nodes_coord_list]

    # Making list of coordinates
    coords_list_df = pddf(coords_list, columns=['lon', 'lat'])
    coords_list_df['geometry'] = (
        coords_list_df.apply(lambda x: Point(x.lon, x.lat), axis=1))
    coords_list_df = coords_list_df.drop(['lon', 'lat'], axis=1)

    # Saving SHP output file
    coords_list_gdf = gpgdf(coords_list_df)
    output_file = Path(args.shp_file)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    # This sets the CRS of the SHP file:
    # Maybe add an option to let the user assign a custom one?
    coords_list_gdf.set_crs(crs="EPSG:4326", inplace=True)
    coords_list_gdf.to_file(f"{output_file}.shp", driver='ESRI Shapefile') # type: ignore
    print(f"\nGeneralized nodes were saved to {args.shp_file}.shp")
    print("\nEND")

elif args.version:
    print(f"Panbiotracks {args.version}")

else:
    print(f"{args.mode} is not a valid option. Please use '-m I', "
          "'-m P' or '-m N', or use '-h' for help.")