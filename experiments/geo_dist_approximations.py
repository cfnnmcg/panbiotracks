import math as mt
import numpy as np
import haversine as hs
import vincenty as vc

er = 6_371.008
x1_lon = -99.15
x1_lat = 19.4
x2_lon = 116.416
x2_lat = 39.916
r = 57.295779

# Trazos2004 Bessel formula
tf = 6378.7 * (np.arccos(mt.sin(19.4/57.2958) * mt.sin(39.916/57.2958) + 
    mt.cos(19.4/57.2958) * mt.cos(39.916/57.2958) * 
    mt.cos((116.416/57.2958)-(-99.15/57.2958))))
print("Trazos2004 Bessel's formula:")
print(f"{tf} km")

# Trazos2004 Bessel formula using Earth's mean radius instead of Ecuator
ts = er * (np.arccos(mt.sin(x1_lat/r) * mt.sin(x2_lat/r) + 
    mt.cos(x1_lat/r) * mt.cos(x2_lat/r) * mt.cos((x2_lon/r)-(x1_lon/r))))
print("\nTrazos2004 Bessel's formula using Earth's mean radius:")
print(f"{float(ts)} km")

# Using haversine package (great-circle distance)
a = (19.4, -99.15)
b = (39.916, 116.416)
print("\nHaversine formula (Python's haversine package):")
print(f"{hs.haversine(a, b)} km")

# Using Vincenty's formula (geodesic ddistance)
print("\nVincenty formula (Python's vincenty package):")
print(f"{vc.vincenty(a, b)} km")