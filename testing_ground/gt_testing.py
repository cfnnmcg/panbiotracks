import os
import math
import numpy as np
import geopandas as gpd
from shapely.geometry import LineString, Point, MultiLineString
from shapely.ops import linemerge, unary_union
import networkx as nx
from scipy.spatial.distance import cdist

# Settings
THRESHOLD_DISTANCE = 5.0      # meters - max distance between parallel segments
THRESHOLD_ANGLE = 30.0        # degrees - max angle deviation for "parallel"
MIN_SEGMENT_LENGTH = 1.0      # meters - ignore very short segments
CONNECTOR_TOLERANCE = 2.0     # meters - tolerance for endpoint matching
MST3_THRESHOLD_SIMILARITY = 0.5

SHAPE1_PATH = "~/Syncthing/qdrive/py_gtracks/tt1.shp"
SHAPE2_PATH = "~/Syncthing/qdrive/py_gtracks/tt2_a.shp"
OUTPUT_PATH = "~/Syncthing/qdrive/py_gtracks/tresult_1-2_a.shp"

def extract_segments(geom):
    """Extract individual line segments from LineString/MultiLineString"""
    segments = []
    if isinstance(geom, LineString):
        coords = list(geom.coords)
        for i in range(len(coords) - 1):
            seg = LineString([coords[i], coords[i+1]])
            if seg.length >= MIN_SEGMENT_LENGTH:
                segments.append(seg)
    elif isinstance(geom, MultiLineString):
        for line in geom.geoms:
            segments.extend(extract_segments(line))
    return segments

def segment_angle(seg):
    """Calculate bearing angle of segment in degrees"""
    if seg.length == 0:
        return 0.0
    coords = list(seg.coords)
    dx = coords[1][0] - coords[0][0]
    dy = coords[1][1] - coords[0][1]
    angle_rad = math.atan2(dy, dx)
    return math.degrees(angle_rad)

def segments_are_parallel(seg1, seg2, max_angle_deg=30.0):
    """Check if two segments are approximately parallel"""
    angle1 = segment_angle(seg1)
    angle2 = segment_angle(seg2)
    angle_diff = min(abs(angle1 - angle2), 180 - abs(angle1 - angle2))
    return angle_diff <= max_angle_deg

def segments_close_enough(seg1, seg2, max_dist):
    """Check if segments are close enough by sampling points"""
    pts1 = np.array(list(seg1.coords))
    pts2 = np.array(list(seg2.coords))
    
    # Sample more points along segments for better distance measurement
    n_samples = max(10, int(min(seg1.length, seg2.length)))
    t1 = np.linspace(0, 1, n_samples)
    t2 = np.linspace(0, 1, n_samples)
    
    pts1_sampled = pts1[0] + t1[:, None] * (pts1[1] - pts1[0])
    pts2_sampled = pts2[0] + t2[:, None] * (pts2[1] - pts2[0])
    
    distances = cdist(pts1_sampled, pts2_sampled)
    min_dist = np.min(distances)
    return min_dist <= max_dist

def midpoint_connector(seg1, seg2):
    """Create connector between midpoints of two segments (case 1)"""
    mid1 = seg1.interpolate(0.5, normalized=True)
    mid2 = seg2.interpolate(0.5, normalized=True)
    return LineString([mid1, mid2])

def angle_bisector_connector(seg1, seg2, overlap_tolerance=CONNECTOR_TOLERANCE):
    """Create angle bisector connector when endpoints overlap (case 2)"""
    # Find overlapping endpoints
    p1a, p1b = Point(list(seg1.coords)[0]), Point(list(seg1.coords)[1])
    p2a, p2b = Point(list(seg2.coords)[0]), Point(list(seg2.coords)[1])
    
    endpoints1 = [p1a, p1b]
    endpoints2 = [p2a, p2b]
    
    # Check which endpoints are close enough
    close_pairs = []
    for i, ep1 in enumerate(endpoints1):
        for j, ep2 in enumerate(endpoints2):
            if ep1.distance(ep2) <= overlap_tolerance:
                close_pairs.append((i, j))
    
    if len(close_pairs) >= 1:
        # Use the first close pair for bisector
        i, j = close_pairs[0]
        anchor1 = endpoints1[i]
        anchor2 = endpoints2[j]
        
        # Angle bisector direction
        v1 = np.array([seg1.coords[1][0] - seg1.coords[0][0], 
                      seg1.coords[1][1] - seg1.coords[0][1]])
        v2 = np.array([seg2.coords[1][0] - seg2.coords[0][0], 
                      seg2.coords[1][1] - seg2.coords[0][1]])
        
        # Unit vectors and bisector
        v1_norm = v1 / np.linalg.norm(v1)
        v2_norm = v2 / np.linalg.norm(v2)
        bisector = v1_norm + v2_norm
        bisector = bisector / np.linalg.norm(bisector)
        
        # Extend from midpoint of anchors
        mid_anchor = anchor1.interpolate(0.5, normalized=False)  # midpoint between anchors
        end_point = Point(mid_anchor.x + bisector[0]*10, mid_anchor.y + bisector[1]*10)
        
        return LineString([mid_anchor, end_point])
    
    return None

def build_mst3(seg1s, seg2s):
    """Build the final MST3 by connecting close/parallel segments"""
    connectors = []
    used_seg1 = set()
    used_seg2 = set()
    
    for i, seg1 in enumerate(seg1s):
        for j, seg2 in enumerate(seg2s):
            if (i in used_seg1) or (j in used_seg2):
                continue
                
            if segments_are_parallel(seg1, seg2, THRESHOLD_ANGLE) and \
               segments_close_enough(seg1, seg2, THRESHOLD_DISTANCE):
                
                # Case 1: midpoint connector (default)
                connector = midpoint_connector(seg1, seg2)
                
                # Case 2: check for angle bisector
                if seg1.distance(seg2) < CONNECTOR_TOLERANCE * 2:  # endpoints close
                    bisector = angle_bisector_connector(seg1, seg2)
                    if bisector and bisector.length > 0:
                        connector = bisector
                
                if connector and connector.length > 0:
                    connectors.append(connector)
                    used_seg1.add(i)
                    used_seg2.add(j)
    
    # Also include all original segments to ensure connectivity
    all_segments = seg1s + seg2s + connectors
    
    # Build MST using networkx (ensures uninterrupted tree)
    G = nx.Graph()
    for i, seg in enumerate(all_segments):
        G.add_node(i, geom=seg)
    
    # Connect segments that are close at endpoints
    for i in range(len(all_segments)):
        for j in range(i+1, len(all_segments)):
            seg_i = all_segments[i]
            seg_j = all_segments[j]
            dist1 = seg_i.boundary.distance(seg_j.boundary)
            if dist1 < CONNECTOR_TOLERANCE:
                G.add_edge(i, j, weight=dist1)
    
    # Extract MST
    if len(G.nodes) > 1:
        mst = nx.minimum_spanning_tree(G, weight='weight')
        mst_segments = []
        for u, v in mst.edges():
            mst_segments.append(all_segments[u])
            mst_segments.append(all_segments[v])
        
        # Merge into single polyline
        final_geom = linemerge(unary_union(mst_segments))
        return final_geom
    
    return unary_union(all_segments)

def main():
    # Load shapefiles
    gdf1 = gpd.read_file(SHAPE1_PATH)
    gdf2 = gpd.read_file(SHAPE2_PATH)
    
    # Extract main geometries
    geom1 = gdf1.geometry.iloc[0] if len(gdf1) > 0 else None
    geom2 = gdf2.geometry.iloc[0] if len(gdf2) > 0 else None

    print(f"geom1: {geom1}")
    print(f"\ngeom2: {geom2}")
    
    if geom1 is None or geom2 is None:
        print("Error: Could not load valid geometries")
        return
    
    # Extract segments from each MST
    seg1s = extract_segments(geom1)
    seg2s = extract_segments(geom2)

    print(f"\nMST1 segments: {len(seg1s)}, MST2 segments: {len(seg2s)}")
    
    print(f"\nseg1s: {seg1s}")
    print(f"seg2s: {seg2s}")
        
    # Build MST3
    mst3 = build_mst3(seg1s, seg2s)
    
    # Save result
    out_gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[mst3], crs=gdf1.crs)
    out_gdf.to_file(OUTPUT_PATH)
    
    print(f"MST3 saved to {OUTPUT_PATH}")
    print(f"Final geometry type: {type(mst3).__name__}")
    print(f"Final length: {mst3.length:.2f}")

if __name__ == "__main__":
    main()