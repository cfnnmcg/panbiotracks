#!/usr/bin/env python3

# Panbiotracks v. 0.3.0
# (c) Carlos Fernando Castillo-García, Universidad Nacional Autónoma de México
# 2023-2026

# This program was made as a fulfillment of the author for obtaining a 
# M.Sc. degree in the Posgrado en Ciencias Biológicas, 
# Universidad Nacional Autónoma de México (UNAM), Mexico. 
# The author thanks the Secretaría de Ciencia, Humanidades, Tecnología e
# Innovación (SECIHTI) for the support of this research through 
# a graduate scholarship.

#import sys
import argparse
import glob
import os
import sys
from itertools import combinations as itcomb

#from pathlib import Path
from geopandas import GeoDataFrame as gpgdf
from geopandas import GeoSeries as gpds
from geopandas import read_file as gprf
from numpy import array as nparr
from numpy import int32 as np32
from pandas import DataFrame as pddf
from pandas import read_csv as pdreadcsv
from shapely.geometry import MultiLineString, Point
from vincenty import vincenty_inverse as vc

from modules import coords_list, edge_list, edges, graph, vertices
from modules.functions import add_edge, add_vertex
from modules.functions import nodes_intersect as ni
from modules.functions import prim_algorithm as prim

#from modules.functions import shp_writer as shpw

# Define program arguments
parser = argparse.ArgumentParser(prog = 'Panbiotracks',
                                 description='Panbiotracks - ' \
                                 'Options, input and output files.')
parser.add_argument('-m', '--mode',
                    choices=['I', 'P', 'N'],
                    help="Set the operation mode: 'I' for individual "
                    "tracks. 'P' for internal generalized tracks. "
                    "'N' for generalized nodes."
                    )
parser.add_argument('-i', '--input',
                    nargs='+',
                    help="Input file or files. "
                    "In individual tracks mode, it must be a single CSV file "
                    "with three columns: species, lat (Latitude) and "
                    "lon (Longitude), in that order. "
                    "For internal generalized tracks and generalized nodes, it "
                    "must be a set of at least two files in the GeoPackage, "
                    "GeoJSON, or SHP formats, separated by a space each. "
                    "It is possible to use a path with a wildcard to process "
                    "all of the files present within a directory "
                    "(i. e. /path/to/files/*.shp)."
                    )
parser.add_argument('-o', '--output',
                    dest='output_fd', 
                    help="For individual tracks, the output is the directory "
                    "where the resulting file or files will be saved. If the "
                    "directory don't exists, it will be created recursively. "
                    "For internal generalized tracks and generalized nodes, "
                    "the output is the name of the resulting file or files, "
                    "without file extension."
                    )
parser.add_argument('-of', '--output_format',
                    choices=['gpkg', 'geojson', 'shp'],
                    help="Optional. Specifies the output file format. "
                    "Use gpkg for GeoPackage, geojson for GeoJSON, "
                    "or shp for ESRI Shapefile. "
                    "If this argument is not used, Panbiotracks will save the "
                    "resulting tracks and nodes in the GeoPackage format."
                    )
parser.add_argument('-v', '--version',
                    action='version',
                    version='%(prog)s 0.3.0',
                    help="Displays the program's version and exits.")
if len(sys.argv)==1:
    parser.print_help()
    # parser.print_usage() # for just the usage line
    parser.exit()
args = parser.parse_args()

#if args.mode == 'I':
def individual_tracks(inputcsv, outputdir, outputformat):
    # INDIVIDUAL TRACKS METHOD
    # Opening CSV file and deleting duplicate records
    print(f"\n{len(inputcsv)} CSV file was loaded. "
          "Building Individual Tracks...")
    
    for i in inputcsv:
        with open(i) as fo:
            df = pdreadcsv(fo, header=0, dtype={'lat': float, 'lon': float})
            df.drop_duplicates(inplace=True)
            list_df = [g for n,g in df.groupby('species')]

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

            # Saving the MST to a SHP file:
            #shpw(f"{args.output_fd}/{filename}") <- Deprecated function.
            it = gpds(MultiLineString(edge_list), crs="epsg:4326")
            
            if outputformat == "gpkg" or outputformat is None:
                fileext = "gpkg"
                ofile = os.path.join(outputdir, filename + '.' + fileext)
                os.makedirs(os.path.dirname(ofile), exist_ok=True)
                it.to_file(ofile, driver="GPKG")

            elif outputformat == "geojson":
                fileext = "geojson"
                ofile = os.path.join(outputdir, filename + '.' + fileext)
                os.makedirs(os.path.dirname(ofile), exist_ok=True)
                it.to_file(ofile, driver="GeoJSON")
            
            elif outputformat == "shp":
                fileext = "shp"
                ofile = os.path.join(outputdir, filename + '.' + fileext)
                os.makedirs(os.path.dirname(ofile), exist_ok=True)
                it.to_file(ofile, driver="ESRI Shapefile")

            print(f"The individual track was saved to "
            f"{outputdir}/{filename}.{fileext}")
            print("\nEND")


# INTERNAL GENERALIZED TRACKS METHOD
#elif args.mode == 'P':
def generalized_tracks(inputfiles, outputfile, outputformat):
    # Global list of input files' paths
    #global edges
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
                    gp_it_list.append(k)
            else:
                print("\nERROR: Panbiotracks needs more than 1 input file "
                      "to perform this function. Add 2 or more files "
                      "after the '-i' option and try again.")
                sys.exit()
    else:
        print(f"\n{len(inputfiles)} input files were loaded. "
              "Building Internal Generalized Track...")
        for i in inputfiles:
            k = gprf(i)
            gp_it_list.append(k)

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
    coords_list_df = pddf(coords_list, columns=["lon", "lat"])
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

    # Saving the MST shapefile
    it = gpds(MultiLineString(edge_list), crs="epsg:4326")
    
    if outputformat == "gpkg" or outputformat is None:
        fileext = "gpkg"
        ofile = os.path.join(outputfile + '.' + fileext)
        os.makedirs(os.path.dirname(ofile), exist_ok=True)
        it.to_file(ofile, driver="GPKG")

    elif outputformat == "geojson":
        fileext = "geojson"
        ofile = os.path.join(outputfile + '.' + fileext)
        os.makedirs(os.path.dirname(ofile), exist_ok=True)
        it.to_file(ofile, driver="GeoJSON")
    
    elif outputformat == "shp":
        fileext = "shp"
        ofile = os.path.join(outputfile + '.' + fileext)
        os.makedirs(os.path.dirname(ofile), exist_ok=True)
        it.to_file(ofile, driver="ESRI Shapefile")

    print(f"\nThe internal generalized track was saved to {outputfile}.{fileext}")
    print("\nEND")


# GENERALIZED NODES METHOD
#elif args.mode == 'N':
def gen_nodes(inputfiles, outputfile, outputformat):
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

    # Making list of coordinates
    coords_list_df = pddf(coords_list, columns=['lon', 'lat'])
    coords_list_df['geometry'] = (
        coords_list_df.apply(lambda x: Point(x.lon, x.lat), axis=1))
    coords_list_df = coords_list_df.drop(['lon', 'lat'], axis=1)

    # Saving SHP output file
    coords_list_gdf = gpgdf(coords_list_df, crs="EPSG:4326")
    
    if outputformat == "gpkg" or outputformat is None:
        fileext = "gpkg"
        ofile = os.path.join(outputfile + '.' + fileext)
        os.makedirs(os.path.dirname(ofile), exist_ok=True)
        coords_list_gdf.to_file(ofile, driver="GPKG")

    elif outputformat == "geojson":
        fileext = "geojson"
        ofile = os.path.join(outputfile + '.' + fileext)
        os.makedirs(os.path.dirname(ofile), exist_ok=True)
        coords_list_gdf.to_file(filename=ofile, driver="GeoJSON")
    
    elif outputformat == "shp":
        fileext = "shp"
        ofile = os.path.join(outputfile + '.' + fileext)
        os.makedirs(os.path.dirname(ofile), exist_ok=True)
        coords_list_gdf.to_file(filename=ofile, driver="ESRI Shapefile")
 
    #output_fd = Path(args.output_fd)
    #output_fd.parent.mkdir(exist_ok=True, parents=True)
    #coords_list_gdf.set_crs(crs="EPSG:4326", inplace=True)
    #coords_list_gdf.to_file(f"{output_fd}.shp", driver='ESRI Shapefile')
    print(f"\nGeneralized nodes were saved to {outputfile}.{fileext}")
    print("\nEND")

def main(workmode, i, o, of):
    if workmode == "I":
        individual_tracks(i, o, of)
    elif workmode == "P":
        generalized_tracks(i, o, of)
    elif workmode == "N":
        gen_nodes(i, o, of)
    
    elif args.version:
        print(f"Panbiotracks {args.version}")
        sys.exit()

    else:
        print(f"{workmode} is not a valid option. Please use '-m I', "
            "'-m P' or '-m N', or use '-h' for help.")

if __name__ == '__main__':
    mode = args.mode
    input = args.input
    output = args.output_fd
    output_format = args.output_format
    main(mode, input, output, output_format)