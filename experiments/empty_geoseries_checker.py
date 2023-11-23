import geopandas as gp
import pandas as pd
import itertools as itt

a = gp.read_file('../outputs/first_tests/e_vestitum.shp')
b = gp.read_file('../outputs/first_tests/m_iltisiana.shp')

inodes = a.intersection(b)
inex = inodes.explode(index_parts = True)

print(inex)
print(inex.is_empty)
print(inex[~inex.is_empty])

if len(inex[~inex.is_empty]) == 0:
    print("Yes")
else:
    print("No")