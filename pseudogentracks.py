import argparse
import sys
import os
import geopandas as gp
import pandas as pd
import numpy as np
import itertools as itt
import matplotlib.pyplot as plt
from vincenty import vincenty_inverse as vc

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

from modules.algorithms import (
    prim_algorithm as primal, add_edge, add_vertex, nodes_intersect)
from modules.shp_writer import shp_writer
from modules import graph, edge_list, edges, coords_list

parser = argparse.ArgumentParser(description='Input and output files.')
parser.add_argument('-i', '--input',
                    dest='it_list',
                    nargs='+',
                    help='List of input SHP files. Needs at least 2.')
parser.add_argument('-o', '--output',
                    dest='shp_file',
                    help="Location and name of the SHP output file, "
                    "without file extension.")
args = parser.parse_args()

gp_it_list = []

for i in args.it_list:
    k = gp.read_file(i)
    gp_it_list.append(k)

for a, b in itt.combinations(gp_it_list, 2):
    nodes_list = nodes_intersect(a, b)
    nodes_coord_list = list(zip(nodes_list.x.astype(float),
        nodes_list.y.astype(float)))
    coords_list = [*coords_list, *nodes_coord_list]
 
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
primal(coords_list_df.shape[0], graph, edges)

coords = coords_list_df.to_numpy()
edges = np.array(edges, dtype=np.int32)
lat = coords[:,0]
lon = coords[:,1]

# Plotting the MST
for e in edges:
    i, j = e
    plt.plot([(coords[i, 1], coords[i, 0]),
    (coords[j, 1], coords[j, 0])], c = 'r')
    edge_list.append([(coords[i, 1], coords[i, 0]),
    (coords[j, 1], coords[j, 0])])

edge_list = list(sorted(edge_list))

# Saving the MST shapefile
shp_writer(args.shp_file)