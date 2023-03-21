import csv
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from vincenty import vincenty_inverse as vc
import shapefile
import amatrix
import prim

# Initialize variables
amatrix.vertices = []
amatrix.vertices_no = 0
amatrix.graph = []
edges = []
edge_list = []

# Initialize files
csv_file = os.path.join(os.path.dirname(__file__), '..', 'assets',
'point_lists', 'antimeridian_test.csv')
shp_file = os.path.join(os.path.dirname(__file__), '..', 'outputs',
'antimeridian_test')
# edges_file = '../outputs/clethra_hartwegii_locs_mst.txt'

# Opening CSV file, deleting duplicate records and converting it to a dataframe
with open(csv_file) as fo:
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
    amatrix.add_vertex(r)

# Adding edges and their weight (lenght)
df_list = df.values.tolist()
for i in range(len(df_list)):
    for j in range(len(df_list)):
        la = tuple(df_list[i])
        lo = tuple(df_list[j])
        amatrix.add_edge(i, j, vc(la, lo))

# Prim function to calculate MST
print("\nDistancias mínimas:")
prim.prim_algorithm(df.shape[0], amatrix.graph, edges)

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

# Saving the MST shapefile
w = shapefile.Writer(shp_file)
w.line(edge_list)
w.field("COMMON_ID", 'C')
w.record("Point")
w.close()
