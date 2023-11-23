#!/usr/bin/env python3

import os
import sys
import argparse
import csv
import pandas as pd
from vincenty import vincenty_inverse as vc
import numpy as np
import matplotlib.pyplot as plt

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

from modules.amatrix import add_edge, add_vertex
from modules.prim import prim_algorithm as primal
from modules.shp_writer import shp_writer
from modules import edge_list, edges, graph

# Define script arguments
parser = argparse.ArgumentParser(description='Input and output files.')
parser.add_argument('-i', '--input',
                    dest='csv_list',
                    nargs='+',
                    help="Input CSV file, with only two columns: "
                    "lat (Latitude) and lon (Longitude), "
                    "in that explicit order.")
parser.add_argument('-o', '--output',
                    dest='shp_file', 
                    help="Location and name of the SHP output "
                    "file, without extension.")
args = parser.parse_args()

files_list = []

for i in args.csv_list:
    files_list.append(i)

for j in files_list:
    with open(j) as fo:
        locs = csv.reader(fo)
        next(locs)
        df = pd.DataFrame(locs, columns=['lat', 'lon'])
        df['lat'] = df['lat'].astype(float)
        df['lon'] = df['lon'].astype(float)
        df.drop_duplicates(inplace=True)

    # Adding vertices
    for r in range(df.shape[0]):
        print(r)
        #add_vertex(r)

    # # Adding edges and their weight (lenght)
    # df_list = df.values.tolist()
    # for i in range(len(df_list)):
    #     for j in range(len(df_list)):
    #         la = tuple(df_list[i])
    #         lo = tuple(df_list[j])
    #         add_edge(i, j, vc(la, lo))

    # # Prim function to calculate MST
    # print("\nMinimal distances:")
    # primal(df.shape[0], graph, edges)

    # # Saving SHP
    # # Making an array from the dataframe and loading graph edges
    # coords = df.to_numpy()
    # edges = np.array(edges, dtype=np.int32)
    # lat = coords[:,0]
    # lon = coords[:,1]
    # # Plotting the MST
    # for e in edges:
    #     i, j = e
    #     plt.plot([(coords[i, 1], coords[i, 0]),
    #     (coords[j, 1], coords[j, 0])], c = 'r')
    #     edge_list.append([(coords[i, 1], coords[i, 0]),
    #     (coords[j, 1], coords[j, 0])])
    # edge_list = list(sorted(edge_list))

    # Saving the MST
    # w = Writer(args.shp_file)
    # w.line(edge_list)
    # w.field("COMMON_ID", 'C')
    # w.record("Point")
    # w.close()
    #shp_writer(args.shp_file)