import geopandas as gp
import pandas as pd
import numpy as np
import shapefile
import matplotlib.pyplot as plt
import adj_matrix
import prim
from vincenty import vincenty_inverse as vc

# Initialize variables
shp_file = "./outputs/gentrack_devo_dou"
adj_matrix.vertices = []
adj_matrix.vertices_no = 0
adj_matrix.graph = []
edges = []
edge_list = []

l1 = gp.read_file("./assets/pinusquercus20_batch/Pinus_devoniana.shp")
l2 = gp.read_file("./assets/pinusquercus20_batch/Pinus_douglasiana.shp")

internodes = l1.intersection(l2)
inex = internodes.explode(index_parts=True)

coords_list = list(zip(inex.x.astype(float), inex.y.astype(float)))
coords_list_df = pd.DataFrame(coords_list, columns=['lon', 'lat'])
coords_list_df = coords_list_df[['lat', 'lon']]

# Adding vertices
for r in range(coords_list_df.shape[0]):
    adj_matrix.add_vertex(r)

# Adding edges and their weight (lenght)
df_list = coords_list_df.values.tolist()
for i in range(len(df_list)):
    for j in range(len(df_list)):
        la = tuple(df_list[i])
        lo = tuple(df_list[j])
        adj_matrix.add_edge(i, j, vc(la, lo))

# Prim function to calculate MST
print("\nDistancias mínimas:")
prim.prim_algorithm(coords_list_df.shape[0], adj_matrix.graph, edges)

# Saving SHP
# Making an array from the dataframe and loading graph edges
coords = coords_list_df.to_numpy()
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
w = shapefile.Writer(shp_file)
w.line(edge_list)
w.field("COMMON_ID", 'C')
w.record("Point")
w.close()
