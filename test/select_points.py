import os
import sys
import geopandas as gpd
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from vincenty import vincenty_inverse as vc
from shapely.geometry import Point

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

from modules.algorithms import (
    prim_algorithm as prim, add_edge, add_vertex)
from modules.shp_writer import shp_writer
from modules import graph, edge_list, edges

output_shp = '../outputs/random_iters/pinus20_test_3'
output_points = '../outputs/random_iters/pinus20_points_test_3.shp'

shp = gpd.read_file('../assets/Pinus_20.shp')
#sample = shp.sample_points(10, method='uniform')
sample_size = 10
iter_num = 10
iter = 0
point_list = []

while iter < iter_num:
    sample_points = shp.sample(sample_size)
    nodes_list = list(zip(sample_points.geometry.x.astype(float),
            sample_points.geometry.y.astype(float)))
    point_list = [*point_list, *nodes_list]
    iter += 1

print(f"Total points: {len(point_list)}\n")

# Making dataframe
coords_list_df = pd.DataFrame(point_list, columns=['lon', 'lat'])
coords_list_df = coords_list_df[['lat', 'lon']]
coords_list_df.drop_duplicates(inplace=True)

geometry = [Point(xy) for xy in zip(coords_list_df.lon, coords_list_df.lat)]
coords_list_df_points = coords_list_df.drop(['lon', 'lat'], axis=1)
coords_list_gdf = gpd.GeoDataFrame(coords_list_df_points, crs="EPSG:4326", 
                                   geometry = geometry)
coords_list_gdf.to_file(output_points)

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
shp_writer(output_shp)

# sample_points = shp.sample(sample_size)
# sample_points.plot()
# plt.show()