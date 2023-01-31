def prim_algorithm(V, graph, edges_list):
    """
    A function that calculates a MST using the Prim's algorithm.
    """
    INF = 9999999
    selected = [0 for value in range(V)]
    no_edge = 0
    selected[0] = True
    print("Arista : Distancia (km)")
    while (no_edge < V - 1):
        minimum = INF
        x = 0
        y = 0
        for i in range(V):
            if selected[i]:
                for j in range(V):
                    if ((not selected[j]) and graph[i][j]):  
                        # not in selected and there is an edge
                        if minimum > graph[i][j]:
                            minimum = graph[i][j]
                            x = i
                            y = j
        print(str(x) + "-" + str(y) + " : " + str(graph[x][y]))
        selected[y] = True
        no_edge += 1
        edges_list.append([x, y])