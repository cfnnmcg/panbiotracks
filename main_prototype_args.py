#!/usr/bin/env python3

import argparse
import csv
import pandas as pd
from vincenty import vincenty_inverse as vc
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import shapefile
import adj_matrix
import prim

# Define script arguments
parser = argparse.ArgumentParser(description='input and output files.')
parser.add_argument('csv_file')
parser.add_argument('shp_file')
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

# Prim function
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

# Create basemap
# map = Basemap(resolution = 'l', projection = 'merc', llcrnrlon = -110.6,
# llcrnrlat = 15.58, urcrnrlon = -87.7, urcrnrlat = 27.7)
# map.drawcoastlines()
# map.drawcountries()
# map.drawmapboundary()
# x,y = map(lon,lat)
# map.plot(x,y,'ro')
# plt.title('Trazo individual')

# Saving edges to file
# with open(edges_file, 'w') as edges_output:
#     for r in edges:
#         s = " ".join(map(str, r))
#         edges_output.write(s+'\n')