import glob
import os
import sys
from itertools import combinations as itcomb

from geopandas import GeoDataFrame as gpgdf
from geopandas import GeoSeries as gpds
from geopandas import read_file as gprf
from numpy import array as nparr
from numpy import int32 as np32
from shapely.geometry import MultiLineString, Point
from vincenty import vincenty_inverse as vc

from modules import coords_list, edge_list, edges, graph, vertices
from modules.functions import add_edge, add_vertex
from modules.functions import nodes_intersect as ni
from modules.functions import prim_algorithm as prim


def individual_tracks(inputcsv, outputdir, outputformat):
    """
    Builds individual tracks from a CSV file and saves them as GeoPackage,
    GeoJSON or ESRI Shapefile.
    """

    # Opening CSV file and deleting duplicate records
    print(f"\n{len(inputcsv)} CSV file(s) loaded. "
          "Building Individual Tracks...")
    
    for i in inputcsv:
        # with open(i) as fo:
        #     df = pdreadcsv(fo, header=0, dtype={'lat': float, 'lon': float})
        #     df.drop_duplicates(inplace=True)
        #     list_df = [g for n,g in df.groupby('species')]

        gdf = gprf(i)
        gdf.drop_duplicates(inplace=True)
        list_df = [g for _,g in gdf.groupby('species')]

        # Iterating over each dataframe:
        for dfi in list_df:

            # Clearing all lists:
            graph.clear()
            vertices.clear()
            edges.clear()
            edge_list.clear()
            coords_list.clear()

            # Adding vertices to the adjacency matrix:
            for r in range(dfi.shape[0]):
                add_vertex(r)

            # Adding edges and their weight (lenght) to the adjacency matrix:
            dfi[['lat', 'lon']] = dfi[['lat', 'lon']].astype('float64')
            df_list = dfi[['lat', 'lon']].values.tolist()
            for i in range(len(df_list)):
                for j in range(len(df_list)):
                    la = tuple(df_list[i])
                    lo = tuple(df_list[j])
                    add_edge(i, j, vc(la, lo))

            # Prim function to calculate MST
            filename = dfi['species'].loc[dfi.index[0]]

            print(f"\n{filename} - Minimal distances between vertices:")
            prim(dfi.shape[0], graph, edges)

            # Making tuples of points to trace edges:
            coords = dfi.to_numpy()
            edges_np = nparr(edges, dtype=np32)
            for e in edges_np:
                i, j = e
                edge_list.append([(coords[i, 2], coords[i, 1]),
                (coords[j, 2], coords[j, 1])])

            # Saving output file:
            it = gpds(MultiLineString(edge_list), crs="epsg:4326")
            
            if outputformat == "gpkg" or outputformat is None:
                fileext = "gpkg"
            elif outputformat == "gjs":
                fileext = "geojson"
            elif outputformat == "shp":
                fileext = "shp"

            ofile = os.path.join(outputdir, filename + '.' + fileext)
            os.makedirs(os.path.dirname(ofile), exist_ok=True)

            if fileext == "gpkg":    
                it.to_file(ofile, driver="GPKG")
            elif fileext == "geojson":
                it.to_file(ofile, driver="GeoJSON")
            elif fileext == "shp":
                it.to_file(ofile, driver="ESRI Shapefile")

            print(f"The individual track was saved to "
            f"{outputdir}/{filename}.{fileext}")
            print("\nCOMPLETED")

def generalized_tracks(inputfiles, outputfile, outputformat):
    """
    Builds an internal generalized track from two or more individual tracks
    files, and saves the IGT as GeoPackage, GeoJSON or ESRI Shapefile.
    """

    global edge_list
    global coords_list
    gp_it_list = []
    
    # Check lenght of input to determine if there's a wildcard:
    if len(inputfiles) < 2:
        for item in inputfiles:
            if item.find('*') > -1:
                pre_it_list = glob.glob(inputfiles.pop(0))
                print(f"\n{len(pre_it_list)} input files were loaded. "
                      "Building Internal Generalized Track...")
                for i in pre_it_list:
                    k = gprf(i)
                    if k.geom_type[0] == "MultiLineString":
                        gp_it_list.append(k)
                    else:
                        print("\nERROR: Some or all of the loaded files "
                        "contain generalized or panbiogeographic nodes."
                        " Check your list of input files and make sure that "
                        "you are loading only individual track files.")
                        sys.exit()
            else:
                print("\nERROR: Panbiotracks needs more than 1 input file "
                      "to perform this function. Add 2 or more files "
                      "after the '-i' flag and try again.")
                sys.exit()
    else:
        print(f"\n{len(inputfiles)} input files were loaded. "
              "Building Internal Generalized Track...")
        for i in inputfiles:
            k = gprf(i)
            if k.geom_type[0] == "MultiLineString":
                gp_it_list.append(k)
            else:
                print("\nERROR: Some or all of the loaded files "
                "contain generalized or panbiogeographic nodes."
                " Check your list of input files and make sure that "
                "you are loading only individual track files.")
                sys.exit()

    # Making intersections
    for a, b in itcomb(gp_it_list, 2):
        nodes_list = ni(a, b)
        if len(nodes_list[~nodes_list.is_empty]) == 0:
            continue
        else:
            nodes_coord_list = list(zip(nodes_list.geometry.x.astype(float),
                nodes_list.geometry.y.astype(float)))
            coords_list = [*coords_list, *nodes_coord_list]

    # Making dataframe
    coords_list_df = gpgdf(coords_list, columns=["lon", "lat"])
    coords_list_df = coords_list_df[['lat', 'lon']]

    # Adding vertices
    for r in range(coords_list_df.shape[0]):
        add_vertex(r)

    # Adding edges and their weight (lenght)
    df_list = coords_list_df.values.tolist()
    for i in range(len(df_list)):
        for j in range(len(df_list)):
            la = tuple(df_list[i])
            lo = tuple(df_list[j])
            add_edge(i, j, vc(la, lo))

    # Prim function to calculate MST
    print("\nMinimal distances between vertices:")
    prim(coords_list_df.shape[0], graph, edges)

    # Making tuples of points to trace edges.
    coords = coords_list_df.to_numpy()
    edges_arr = nparr(edges, dtype=np32)
    for e in edges_arr:
        i, j = e
        edge_list.append([(coords[i, 1], coords[i, 0]),
        (coords[j, 1], coords[j, 0])])
    edge_list = sorted(edge_list)

    # Saving output file
    it = gpds(MultiLineString(edge_list), crs="epsg:4326")
    
    if outputformat == "gpkg" or outputformat is None:
        fileext = "gpkg"
    elif outputformat == "gjs":
        fileext = "geojson"
    elif outputformat == "shp":
        fileext = "shp"

    ofile = os.path.join(outputfile + '.' + fileext)
    os.makedirs(os.path.dirname(ofile), exist_ok=True)
    
    if fileext == "gpkg":
        it.to_file(ofile, driver="GPKG")
    elif fileext == "geojson":
        it.to_file(ofile, driver="GeoJSON")
    elif fileext == "shp":
        it.to_file(ofile, driver="ESRI Shapefile")

    print(f"\nThe internal generalized track was saved to {outputfile}.{fileext}")
    print("\nCOMPLETED")

def gen_nodes(inputfiles, outputfile, outputformat):
    """
    Find generalized nodes based on the intersections between two or more
    generalized tracks, and saves them as GeoPackage, GeoJSON or ESRI Shapefile
    """

    # Global list of generalized tracks
    global coords_list
    gt_gp_list = []
    
    # Check lenght of input to determine if there's a wildcard:
    if len(inputfiles) < 2:
        for item in inputfiles:
            if item.find('*') > -1:
                pre_it_list = glob.glob(inputfiles.pop(0))
                print(f"\n{len(pre_it_list)} input files were loaded. "
                      "Finding Generalized Nodes...")
                for i in pre_it_list:
                    k = gprf(i)
                    if k.geom_type[0] == "MultiLineString":
                        gt_gp_list.append(k)
                    else:
                        print("\nERROR: Some or all of the loaded files "
                        "already contain generalized or panbiogeographic nodes."
                        " Check your list of input files and make sure that "
                        "you are loading only generalized track files.")
                        sys.exit()
            else:
                print("\nERROR: Panbiotracks needs more than 1 input file "
                      "to perform this function. Add 2 or more files "
                      "after the '-i' flag and try again.")
                sys.exit()
    else:
        print(f"\n{len(inputfiles)} SHP files were loaded. "
              "Finding Generalized Nodes...")
        for i in inputfiles:
            k = gprf(i)
            if k.geom_type[0] == "MultiLineString":
                gt_gp_list.append(k)
            else:
                print("\nERROR: Some or all of the loaded files "
                "already contain generalized or panbiogeographic nodes."
                " Check your list of input files and make sure that "
                "you are loading only generalized track files.")
                sys.exit()

    # Finding intersections
    for a, b in itcomb(gt_gp_list, 2):
        nodes_list = ni(a, b)
        if len(nodes_list[~nodes_list.is_empty]) == 0:
            continue
        else:
            nodes_coord_list = list(zip(nodes_list.geometry.x.astype(float),
                nodes_list.geometry.y.astype(float)))
            coords_list = [*coords_list, *nodes_coord_list]

    # Creating GeoDataframe to export
    c = [Point(coord[0], coord[1]) for coord in coords_list]
    coords_list_gdf = gpgdf(coords_list, columns=['lon', 'lat'], geometry=c, crs="EPSG:4326")
    coords_list_gdf = coords_list_gdf.drop(['lon', 'lat'], axis=1)
    
    # Saving output file
    if outputformat == "gpkg" or outputformat is None:
        fileext = "gpkg"
    elif outputformat == "gjs":
        fileext = "geojson"
    elif outputformat == "shp":
        fileext = "shp"

    ofile = os.path.join(outputfile + '.' + fileext)
    os.makedirs(os.path.dirname(ofile), exist_ok=True)
        
    if fileext == "gpkg":
        coords_list_gdf.to_file(ofile, driver="GPKG")
    if fileext == "geojson":
        coords_list_gdf.to_file(filename=ofile, driver="GeoJSON")
    if fileext == "shp":
        coords_list_gdf.to_file(filename=ofile, driver="ESRI Shapefile")
 
    print(f"\nGeneralized nodes were saved to {outputfile}.{fileext}")
    print("\nCOMPLETED")