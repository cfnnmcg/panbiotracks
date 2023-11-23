import os
import sys
import geopandas as gpd
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from vincenty import vincenty_inverse as vc
from pybind11_rdp import rdp
from simplification.cutil import simplify_coords_vw

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

from modules.functions import (
    prim_algorithm as prim, add_edge, add_vertex)
from modules.shp_writer import shp_writer
from modules import graph, edge_list, edges

input_shp = '../outputs/random_iters/pinus20_points_test_2.shp'
output_shp = '../outputs/random_iters/pinus20_test_2_simp-vw_10-0'

shp = gpd.read_file(input_shp)
shp_p_list = list(zip(shp.geometry.x.astype(float),
                      shp.geometry.y.astype(float)))
shp_p_np = np.array(shp_p_list, dtype='float')

# USING pybind11-rdp
simp = rdp(shp_p_np, epsilon=1)

# USING simplification Visvalingam-Whyatt
#simp = simplify_coords_vw(shp_p_np, 10.0)

print(f"Número de puntos iniciales: {len(shp_p_np)}\n")
print(f"Número de puntos finales: {len(simp)}")
print(simp)

simp_graph_df = pd.DataFrame(simp, columns = ['lon', 'lat'])
simp_graph_df = simp_graph_df[['lat', 'lon']]

# Adding vertices
for r in range(simp_graph_df.shape[0]):
    add_vertex(r)

# Adding edges and their weight (lenght)
df_list = simp_graph_df.values.tolist()
for i in range(len(df_list)):
    for j in range(len(df_list)):
        la = tuple(df_list[i])
        lo = tuple(df_list[j])
        add_edge(i, j, vc(la, lo))

# Prim function to calculate MST
print("\nDistancias mínimas:")
prim(simp_graph_df.shape[0], graph, edges)

# Making tuples of points to trace edges.
coords = simp_graph_df.to_numpy()
edges = np.array(edges, dtype=np.int32)
for e in edges:
    i, j = e
    edge_list.append([(coords[i, 1], coords[i, 0]),
    (coords[j, 1], coords[j, 0])])
edge_list = list(sorted(edge_list))

# Saving the MST shapefile
shp_writer(output_shp)



"""
arr = np.array([(1, 1), (2, 3), (3, 4), (4, 6)])
print(arr)
mask = rdp(arr, epsilon=0.5, algo="iter", return_mask=True)
print(mask)
print(arr[mask])
"""