import math
import numpy as np
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString
from shapely import LineString, Point, distance as shapely_distance, equals, equals_exact
import itertools
from scipy.sparse import csgraph
from scipy.spatial.distance import squareform
import networkx as nx


def angle_between_lines(ls1, ls2, tol_deg=1e-6):
    """Compute the smallest angle in degrees between two LineStrings."""
    # Get unit vectors along the segments
    def dir_vec(ls):
        coords = np.array(ls.coords)
        v = coords[-1] - coords[0]
        norm = np.linalg.norm(v)
        if norm < tol_deg:
            return np.zeros(2)
        return v / norm

    v1 = dir_vec(ls1)
    v2 = dir_vec(ls2)
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0.0
    cos_a = np.clip(np.dot(v1, v2), -1.0, 1.0)
    angle_rad = np.arccos(cos_a)
    return math.degrees(angle_rad)


def perpendicular_bisector(ls1, ls2, d, a):
    """If two lines are close and angle ≤ a, return a segment on the angle bisector."""
    coords1 = np.array(ls1.coords)
    coords2 = np.array(ls2.coords)
    mid1 = (coords1[0] + coords1[-1]) / 2.0
    mid2 = (coords2[0] + coords2[-1]) / 2.0
    mid_mid = (mid1 + mid2) / 2.0

    # Unit direction of each line
    v1 = coords1[-1] - coords1[0]
    v2 = coords2[-1] - coords2[0]
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 < 1e-10 or n2 < 1e-10:
        return None

    u1 = v1 / n1
    u2 = v2 / n2

    # Unoriented bisector direction
    bisector = u1 + u2
    norm_b = np.linalg.norm(bisector)
    if norm_b < 1e-10:
        return None
    bisector = bisector / norm_b

    # Create a bisector segment roughly centered
    length = max(n1, n2)
    end1 = mid_mid - 0.5 * length * bisector
    end2 = mid_mid + 0.5 * length * bisector
    mid_seg = LineString([tuple(end1), tuple(end2)])

    # Re‑clip so that it “follows” the orientation of the two lines
    # (you can refine this if you want a specific length)
    return mid_seg


def compute_mst3(edges_g1, edges_g2, d, a, tol=1e-6):
    """Build MST3 from congruent edges between MST1 and MST2."""
    mst3_segments = []  # List of LineString segments
    used_e1 = set()
    used_e2 = set()

    # Flat list of edges with index
    list1 = list(enumerate(edges_g1))
    list2 = list(enumerate(edges_g2))

    for i, seg1 in list1:
        best_match = None
        best_dist = float("inf")
        best_angle = 180.0

        for j, seg2 in list2:
            if j in used_e2:
                continue

            # Get closest distance between the two segments
            dist = shapely_distance(seg1, seg2)

            # Compute angle between them
            angle = angle_between_lines(seg1, seg2)

           # Only consider segments that satisfy both angle and distance thresholds
            if angle <= a and dist <= d:
                if dist < best_dist or (dist == best_dist and angle < best_angle):
                    best_match = (i, j)
                    best_dist = dist
                    best_angle = angle

        if best_match is None:
            # Too far or too different angle: skip
            continue

        if best_match is not None:
            _, j = best_match
            seg1, seg2 = edges_g1[i], edges_g2[j]
            coords1 = seg1.coords[:]
            coords2 = seg2.coords[:]

            # Case 1: overlapping (same line or very close geometry)
            if equals_exact(seg1, seg2, tolerance=tol):
                mst3_segments.append(seg1)
                used_e1.add(i)
                used_e2.add(j)
                continue

            # Case 2: parallel or quasi‑parallel and close
            if best_angle <= 15.0 and dist <= d:
                # Only construct mid‑line if distance is small
                mid_coords = [
                    ((coords1[k][0] + coords2[k][0]) / 2.0,
                     (coords1[k][1] + coords2[k][1]) / 2.0)
                    for k in range(len(coords1))
                ]
                mid_seg = LineString(mid_coords)
                mst3_segments.append(mid_seg)
                used_e1.add(i)
                used_e2.add(j)
                continue

            # Case 3: non‑parallel but similar angle and close
            if best_angle <= a and dist <= d:
                mid_seg = perpendicular_bisector(seg1, seg2, d, a)
                if mid_seg is not None:
                    mst3_segments.append(mid_seg)
                    used_e1.add(i)
                    used_e2.add(j)

        else:
            # Too far or too different angle: mark as not congruent
            pass

    if len(mst3_segments) == 0:
        return None, 0.0

    # Build a graph from the mid‑segments (MST3 candidate)
    # nodes are the endpoints of the segments
    G = nx.Graph()
    endpoint_to_node = {}

    for seg in mst3_segments:
        start = tuple(seg.coords[0])
        end = tuple(seg.coords[-1])

        for pt in [start, end]:
            if pt not in endpoint_to_node:
                endpoint_to_node[pt] = len(endpoint_to_node)

        u = endpoint_to_node[start]
        v = endpoint_to_node[end]
        length = seg.length
        if u != v:
            G.add_edge(u, v, weight=length)

    if len(G.edges) == 0:
        return None, 0.0

    # Compute MST3 on this induced graph
    T = nx.minimum_spanning_tree(G)
    mst3_lines = []
    node_to_coord = {v: k for k, v in endpoint_to_node.items()}

    for u, v in T.edges:
        coords = [node_to_coord[u], node_to_coord[v]]
        mst3_lines.append(LineString(coords))

    # Compute congruence: fraction of edges in MST1 that have a congruent pair in MST2
    num_congruent = len(used_e1)
    total_e1 = len(edges_g1)
    if total_e1 == 0:
        similarity = 0.0
    else:
        similarity = num_congruent / total_e1

    return mst3_lines, similarity


def main(mst1_shp, mst2_shp, mst3_shp, d, a_deg):
    # Load the two MSTs as GeoDataFrames
    gdf1 = gpd.read_file(mst1_shp)
    gdf2 = gpd.read_file(mst2_shp)

    # --- DEBUG: show geometry types in MST1 ---
    print("MST1 geometry types:")
    print(gdf1.geometry.geom_type.value_counts())

    # --- DEBUG: show geometry types in MST2 ---
    print("MST2 geometry types:")
    print(gdf2.geometry.geom_type.value_counts())
    # ------------------------------------------

    # Flatten all line‑like geometries from MST1 (LineString + MultiLineString)
    lines1 = []
    for geom in gdf1.geometry:
        if geom.geom_type == "LineString":
            lines1.append(geom)
        elif geom.geom_type == "MultiLineString":
            for line in geom.geoms:
                lines1.append(line)

    if len(lines1) == 0:
        print("MST1 has no (Multi)LineString geometries; cannot build MST edges.")
        print("Actual geometry types:", gdf1.geometry.geom_type.unique())
        return

    # Do the same for MST2
    lines2 = []
    for geom in gdf2.geometry:
        if geom.geom_type == "LineString":
            lines2.append(geom)
        elif geom.geom_type == "MultiLineString":
            for line in geom.geoms:
                lines2.append(line)

    if len(lines2) == 0:
        print("MST2 has no (Multi)LineString geometries.")
        return

    # --- DEBUG: show how many edges you actually have ---
    print(f"MST1 has {len(lines1)} line segments.")
    print(f"MST2 has {len(lines2)} line segments.")
    # -----------------------------------------------------

    # Compute MST3 and similarity
    mst3_lines, similarity = compute_mst3(
        edges_g1=lines1,
        edges_g2=lines2,
        d=d,                 # distance threshold (e.g., meters)
        a=a_deg              # angular threshold in degrees
    )

    if mst3_lines is None:
        print("MST1 and MST2 are too dissimilar; no MST3 built.")
        print(f"Similarity: {similarity:.3f}")
        return

    print(f"Similarity between MST1 and MST2: {similarity:.3f}")
    print(f"Number of edges in MST3: {len(mst3_lines)}")

    # Create a GeoDataFrame for MST3
    mst3_gdf = gpd.GeoDataFrame(
        {"geometry": mst3_lines},
        crs=gdf1.crs  # preserve CRS of MST1
    )

    # print(gdf1.to_string())
    # print(f"\n{gdf2.to_string()}")
    # print(f"\n{mst3_gdf.to_string()}")

    # Save MST3 to a shapefile
    mst3_gdf.to_file(mst3_shp)


# Example call (tune d, a according to your CRS units and tolerance)
if __name__ == "__main__":
    mst1_shp = "~/Syncthing/qdrive/py_gtracks/tt1.shp"   # MST1 shapefile
    mst2_shp = "~/Syncthing/qdrive/py_gtracks/tt3.shp"   # MST2 shapefile
    mst3_shp = "~/Syncthing/qdrive/py_gtracks/tresult_1-3.shp"  # output MST3

    # Distance threshold (in same units as your CRS, e.g., meters if projected)
    d_threshold = 1500.0

    # Angular threshold (degrees)
    a_deg_threshold = 10.0

    main(mst1_shp, mst2_shp, mst3_shp, d_threshold, a_deg_threshold)