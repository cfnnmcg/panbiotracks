def add_vertex(v):
    """
    Adds vertices to an adjacency matrix, as many as locations are in the CSV.
    """
    global graph
    global vertices_no
    global vertices
    if v in vertices:
        print("Vertex ", v, "already exists.")
    else:
        vertices_no = vertices_no + 1
        vertices.append(v)
        if vertices_no > 1:
            for vertex in graph:
                vertex.append(0)
        temp = []
        for i in range(vertices_no):
            temp.append(0)
        graph.append(temp)

def add_edge(v1, v2, e):
    """
    Adds edges and their weight (lenght) to the adjacency matrix.
    """
    global graph
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
        graph[index1][index2] = e