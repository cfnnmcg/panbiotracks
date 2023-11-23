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

from modules.functions import prim_algorithm as primal, add_edge, add_vertex, nodes_intersect
from modules.shp_writer import shp_writer
from modules import graph, edge_list, edges, coords_list

it1 = gp.read_file("../outputs/first_tests/c_alcoceri.shp")
it2 = gp.read_file("../outputs/first_tests/c_hartwegii.shp")
it3 = gp.read_file("../outputs/first_tests/e_vestitum.shp")
it4 = gp.read_file("../outputs/first_tests/m_iltisiana.shp")

shp_file = ("../outputs/first_tests/gt_points/gt_alco_hart_vest")

it_list = [it1, it2, it3, it4]

ls = [type(i) for i in it_list]
print(ls)

for a, b in itt.combinations(it_list, 2):
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
shp_writer(shp_file)
