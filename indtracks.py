#!/usr/bin/env python3

import argparse
import pandas as pd
from vincenty import vincenty_inverse as vc
import numpy as np
from modules.amatrix import add_edge, add_vertex
from modules.prim import prim_algorithm as prim
from modules.shp_writer import shp_writer
from modules import edge_list, edges, graph

# Define script arguments
parser = argparse.ArgumentParser(description='Input and output files.')
parser.add_argument('-i', '--input',
                    dest='csv_file',
                    help="Input CSV file, with only two columns: "
                    "lat (Latitude) and lon (Longitude), "
                    "in that explicit order.")
parser.add_argument('-o', '--output',
                    dest='shp_file', 
                    help="Location and name of the SHP output "
                    "file, without extension.")
args = parser.parse_args()

# Opening CSV file and deleting duplicate records
with open(args.csv_file) as fo:
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
shp_writer(args.shp_file)
