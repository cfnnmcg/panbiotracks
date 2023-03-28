import geopandas as gp
import pandas as pd
import itertools as itt
from vincenty import vincenty_inverse as vc
from modules.prim import prim_algorithm as pa

it1 = gp.read_file("../outputs/first_tests/c_alcoceri.shp")
it2 = gp.read_file("../outputs/first_tests/c_hartwegii.shp")
it3 = gp.read_file("../outputs/first_tests/e_vestitum.shp")

it_list = [it1, it2, it3]

vertices = []
matr = []
vertices_n = 0
edges = []
edge_list = []

def add_vertices(v):
    global vertices_n
    global vertices
    global matr
    vertices_n = vertices_n + 1
    vertices.append(v)
    if vertices_n > 1:
        for vertex in matr:
            vertex.append(0)
    t = []
    for i in range(vertices_n):
        t.append(0)
    matr.append(t)

def add_edge(v1, v2, e):
    """
    Adds edges and their weight (lenght) to the adjacency matrix.
    """
    global matr
    global vertices_no
    global vertices
    # Check if vertex v1 is a valid vertex
    if v1 not in vertices:
        print("Vertex ", v1, " does not exists.")
    # Check if vertex v2 is a valid vertex
    elif v2 not in vertices:
        print("Vertex ", v2, " does not exists.")
    else:
        index1 = vertices.index(v1)
        index2 = vertices.index(v2)
        matr[index1][index2] = e

def nodes_intersect(n1, n2):
    internodes = n1.intersection(n2)
    inex = internodes.explode(index_parts = True)
    return inex

for a, b in itt.combinations(it_list, 2):
    nodes_list = nodes_intersect(a, b)
    coords_list = list(zip(nodes_list.x.astype(float),
        nodes_list.y.astype(float)))
    coords_list_df = pd.DataFrame(coords_list, columns=['lon', 'lat'])
    coords_list_df = coords_list_df[['lat', 'lon']]
    for r in range(coords_list_df.shape[0]):
        add_vertices(r)
    df_list = coords_list_df.values.tolist()
    for i in range(len(df_list)):
        for j in range(len(df_list)):
            la = tuple(df_list[i])
            lo = tuple(df_list[j])
            add_edge(i, j, vc(la, lo))
    pa(coords_list_df.shape[0], matr, edges)

# for r in it_list:
#     add_vertices(r)

# for i in range(len(it_list)):
#     for j in range(len(it_list)):
#         a1 = it_list[i]
#         a2 = it_list[j]
#         add_edge(i, j, nodes_intersect(a1, a2))

# print(it_list)
# print(matr)
