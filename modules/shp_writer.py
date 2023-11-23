from shapefile import Writer
from modules import edge_list

def shp_writer(f):
    '''
    A simple function that uses a list of edges to write a SHP file.
    '''
    global edge_list
    w = Writer(f)
    w.line(edge_list)
    w.field("COMMON_ID", 'C')
    w.record("Point")
    w.close()