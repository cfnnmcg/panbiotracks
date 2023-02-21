#!/usr/bin/env python3

import argparse
import csv
import pandas as pd
from vincenty import vincenty_inverse as vc
import numpy as np
import matplotlib.pyplot as plt
import shapefile
import adj_matrix
import prim

# Define script arguments
parser = argparse.ArgumentParser(description='input and output files.')
parser.add_argument('csv_file', help="Input CSV file, with only two columns:"
    "lat (Latitude) and lon (Longitude), in that order")
parser.add_argument('shp_file', help="Location and name of the SHP output file")
args = parser.parse_args()

# Initialize variables
adj_matrix.vertices = []
adj_matrix.vertices_no = 0
adj_matrix.graph = []
edges = []
edge_list = []

# Opening CSV file, deleting duplicate records and converting it to a dataframe
with open(args.csv_file) as fo:
    locs = csv.reader(fo)
    next(locs)
    df = pd.DataFrame(locs, columns=['lat', 'lon'])
    df.drop_duplicates(inplace=True)
    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)
print(f"Dataframe:")
print(f"{df}\n")

# Adding vertices
for r in range(df.shape[0]):
    adj_matrix.add_vertex(r)

# Adding edges and their weight (lenght)
df_list = df.values.tolist()
for i in range(len(df_list)):
    for j in range(len(df_list)):
        la = tuple(df_list[i])
        lo = tuple(df_list[j])
        adj_matrix.add_edge(i, j, vc(la, lo))

# Prim function to calculate MST
print("\nDistancias mínimas:")
prim.prim_algorithm(df.shape[0], adj_matrix.graph, edges)

# Saving SHP
# Making an array from the dataframe and loading graph edges
coords = df.to_numpy()
edges = np.array(edges, dtype=np.int32)
    
# Loading coordinates
lat = coords[:,0]
lon = coords[:,1]

# Plotting the MST
for e in edges:
    i, j = e
    plt.plot([(coords[i, 1], coords[i, 0]),
    (coords[j, 1], coords[j, 0])], c = 'r')
    edge_list.append([(coords[i, 1], coords[i, 0]),
    (coords[j, 1], coords[j, 0])])
# plt.show()

# Sort the list of edges
edge_list = list(sorted(edge_list))

# Save the minimum spanning tree
w = shapefile.Writer(args.shp_file)
w.line(edge_list)
w.field("COMMON_ID", 'C')
w.record("Point")
w.close()
