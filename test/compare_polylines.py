import numpy as np
from scipy import interpolate as ipl
from matplotlib import pyplot as plt

def normed_distance_along_path( polyline ):
    polyline = np.asarray(polyline)
    distance = np.cumsum( np.sqrt(np.sum( np.diff(polyline, axis=1)**2, axis=0 )) )
    return np.insert(distance, 0, 0)/distance[-1]

def average_distance_between_polylines(xy1, xy2):   
    s1 = normed_distance_along_path(xy1)
    s2 = normed_distance_along_path(xy2)

    interpol_xy1 = ipl.interp1d( s1, xy1 )
    xy1_on_2 = interpol_xy1(s2)

    node_to_node_distance = np.sqrt(np.sum( (xy1_on_2 - xy2)**2, axis=0 ))

    print(node_to_node_distance.mean()) # or use the max

# Two example polyline:
xy1 = [0, 1, 8, 2, 1.7],  [1, 0, 6, 7, 1.9]   # it should work in 3D too
xy2 = [.1, .6, 4, 8.3, 2.1, 2.2, 2],  [.8, .1, 2, 6.4, 6.7, 4.4, 2.3]

fig, ax1 = plt.subplots()
ax1.plot(xy2)
plt.show()

average_distance_between_polylines(xy1, xy2)  # 0.45004578069119189
