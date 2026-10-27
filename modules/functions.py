#!/usr/bin/env python3

#from shapefile import Writer

import numpy as np

from modules import graph, vertices  #, vertices_n

vertices_n = 0

def add_vertex(v):
    """
    Adds vertices to an adjacency matrix, as many as locations are in the CSV.
    """
    # global graph
    global vertices_n
    # global vertices

    if v in vertices:
        print("Vertex ", v, "already exists.")
    else:
        vertices_n = vertices_n + 1
        vertices.append(v)
        if vertices_n > 1:
            for vertex in graph:
                vertex.append(0)
        temp = []
        for i in range(vertices_n):
            temp.append(0)
        graph.append(temp)

def add_edge(v1, v2, e):
    """
    Adds edges and their weight (lenght) to the adjacency matrix.
    """
    # global graph
    # global vertices_n
    # global vertices
    # Check if vertex v1 is a valid vertex
    if v1 not in vertices:
        print("Vertex ", v1, " does not exists.")
    # Check if vertex v2 is a valid vertex
    elif v2 not in vertices:
        print("Vertex ", v2, " does not exists.")
    else:
        index1 = vertices.index(v1)
        index2 = vertices.index(v2)
        graph[index1][index2] = e

def prim_algorithm(V, graph, edges_list):
    """
    A function that calculates a MST using the Prim's algorithm.
    """
    INF = 9999999
    selected = [0 for value in range(V)]
    no_edge = 0
    selected[0] = True
    print("Edge : Lenght (km)")
    while (no_edge < V - 1):
        minimum = INF
        x = 0
        y = 0
        for i in range(V):
            if selected[i]:
                for j in range(V):
                    if ((not selected[j]) and graph[i][j] and minimum > graph[i][j]):  
                        # not in selected and there is an edge
                        minimum = graph[i][j]
                        x = i
                        y = j
        print(str(x) + "-" + str(y) + " : " + str(graph[x][y]))
        selected[y] = True
        no_edge += 1
        edges_list.append([x, y])

def nodes_intersect(n1, n2):
    '''
    Checks for all of the intersection points between 2 individual
    tracks and returns a list of coordinates of such points.
    '''
    internodes = n1.intersection(n2)    
    inex = internodes.extract_unique_points().explode(
        index_parts = True).droplevel(0)
    return inex

def mls_coords(geom):
    """Return all vertices of a Shapely MultiLineString as an (N, 2) array."""
    coords = []
    for line in geom.geoms:
        coords.extend(line.coords)
    return np.asarray(coords, dtype=float)

def principal_axis(geom):
    """
    Return the unit vector of the first principal component
    of a MultiLineString geometry.
    """
    xy = mls_coords(geom)
    if len(xy) < 2:
        raise ValueError("A geometry has fewer than two vertices.")
    xy_centered = xy - xy.mean(axis=0)
    _, _, vt = np.linalg.svd(xy_centered, full_matrices=False)
    axis = vt[0]
    return axis / np.linalg.norm(axis)

def orientation_distance(axis_i, axis_j):
    """
    Return orientation dissimilarity. Ignores direction.
    """
    cosine = np.dot(axis_i, axis_j)
    return 1.0 - abs(cosine)