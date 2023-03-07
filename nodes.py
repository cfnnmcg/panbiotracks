import geopandas as gp

# Importar trazos generalizados
l1 = gp.read_file("./assets/pinusquercus20_batch/Pinus_arizonica.shp")
l2 = gp.read_file("./assets/pinusquercus20_batch/Pinus_ayacahuite.shp")

#Buscar intersección
def find_nodes(t1, t2, filename):
    inter = t1.intersection(t2)
    inter.to_file(filename)

find_nodes(l1, l2, "./outputs/nodes_t1-t2")
