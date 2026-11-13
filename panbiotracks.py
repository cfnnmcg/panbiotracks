#!/usr/bin/env python3

# Panbiotracks v. 0.4.0
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
import sys

from modules.methods import (
    gen_nodes,
    generalized_tracks,
    geometric_similarity,
    individual_tracks,
)


def check_positive(value):
    try:
        value = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{value} is an invalid value. It must be a decimal number "
            "between 0 and 1."
        )
    if (value < 0.0 or value > 1.0):
        raise argparse.ArgumentTypeError(f"{value} is an invalid value. "
        "Threshold value must be a decimal number between 0 and 1.")
    return value

# Define program arguments
parser = argparse.ArgumentParser(prog = 'Panbiotracks',
                                 description='Panbiotracks - ' \
                                 'Options, input and output files.')
subparsers = parser.add_subparsers(
    dest="mode",
    required=True,
    metavar="MODE"
)

parser_i = subparsers.add_parser("I",
                    help="Builds individual tracks from a list of geographic "
                    "coordinates.")
parser_i.add_argument('-i', '--input', required=True,
                    nargs='+',
                    help="A single CSV file with three columns: "
                    "species, lat (latitude) and lon (longitude), "
                    "in that order.")
parser_i.add_argument('-o', '--output', required=True,
                    dest='output_fd',
                    help="Path and name of the destination folder.")
parser_i.add_argument('-of', '--output_format',
                    choices=['gpkg', 'gjs', 'shp'],
                    help="Optional. Specifies the output file format. "
                    "Use gpkg for GeoPackage, gjs for GeoJSON, "
                    "or shp for ESRI Shapefile. "
                    "If this argument is not used, Panbiotracks will save the "
                    "resulting tracks and nodes in the GeoPackage format.")

parser_p = subparsers.add_parser("P",
                    help="Builds an internal generalized track from a set "
                    "of individual tracks.")
parser_p.add_argument('-i', '--input', required=True,
                    nargs='+',
                    help="Input files. "
                    "A set of at least two files in the GeoPackage, "
                    "GeoJSON, or SHP formats, separated by a space each. "
                    "It is possible to use a path with a wildcard to process "
                    "all of the files present within a directory "
                    "(i. e. /path/to/files/*.shp).")
parser_p.add_argument('-o', '--output', required=True,
                    dest='output_fd',
                    help="Path and name of the destination file, "
                    "without file extension.")
parser_p.add_argument('-of', '--output_format',
                    choices=['gpkg', 'gjs', 'shp'],
                    help="Optional. Specifies the output file format. "
                    "Use gpkg for GeoPackage, gjs for GeoJSON, "
                    "or shp for ESRI Shapefile. "
                    "If this argument is not used, Panbiotracks will save the "
                    "resulting tracks and nodes in the GeoPackage format.")

parser_n = subparsers.add_parser("N",
                    help="Builds a set of generalized nodes from a set of "
                    "generalized or internal generalized tracks.")
parser_n.add_argument('-i', '--input', required=True,
                    nargs='+',
                    help="Input files. "
                    "A set of at least two files in the GeoPackage, "
                    "GeoJSON, or SHP formats, separated by a space each. "
                    "It is possible to use a path with a wildcard to process "
                    "all of the files present within a directory "
                    "(i. e. /path/to/files/*.shp).")
parser_n.add_argument('-o', '--output', required=True,
                    dest='output_fd',
                    help="Path and name of the destination file, "
                    "without file extension.")
parser_n.add_argument('-of', '--output_format',
                    choices=['gpkg', 'gjs', 'shp'],
                    help="Optional. Specifies the output file format. "
                    "Use gpkg for GeoPackage, gjs for GeoJSON, "
                    "or shp for ESRI Shapefile. "
                    "If this argument is not used, Panbiotracks will save the "
                    "resulting tracks and nodes in the GeoPackage format.")

parser_g = subparsers.add_parser("G",
                    help="Experimental function to find geometric "
                    "congruence between individual tracks.")
parser_g.add_argument('-i', '--input', required=True,
                    nargs='+',
                    help="Input files. "
                    "A set of at least two files in the GeoPackage, "
                    "GeoJSON, or SHP formats, separated by a space each. "
                    "It is possible to use a path with a wildcard to process "
                    "all of the files present within a directory "
                    "(i. e. /path/to/files/*.shp).")
parser_g.add_argument('-st', '--similarity_threshold',
                    type=check_positive,
                    default=0.1,
                    help="Similarity threshold. A decimal value from 0 to 1, "
                    "where 0 equals to max similarity between tracks, and "
                    "1 equals to max dissimilarity. The default value is 0.1.")
parser_g.add_argument('-dt', '--distance_threshold',
                    type=check_positive,
                    default=0.1,
                    help="Centroid threshold. A decimal value from 0 to 1, "
                    "where 0 equals to min distance between tracks, and "
                    "1 equals to max distance. The default value is 0.1.")
parser_g.add_argument('-ot', '--orientation_threshold',
                    type=check_positive,
                    default=0.1,
                    help="Orientation threshold. A decimal value from 0 to 1, "
                    "where 0 means that track A and track B have the same "
                    "orientation (they share the same angle), while 1 means "
                    "they are perpendicular (they form a 90 degree angle). "
                    "The default value is 0.1.")

parser.add_argument('-v', '--version',
                    action='version',
                    version='%(prog)s 0.4.0',
                    help="Display the program's version and exit.")
if len(sys.argv)==1:
    parser.print_help()
    # parser.print_usage() # for just the usage line
    parser.exit()
args = parser.parse_args()


if __name__ == '__main__':
    mode = args.mode
    input = args.input

    if mode == "I":
        individual_tracks(input, args.output_fd, args.output_format)
    elif mode == "P":
        generalized_tracks(input, args.output_fd, args.output_format)
    elif mode == "N":
        gen_nodes(input, args.output_fd, args.output_format)
    elif mode == "G":
        st = args.similarity_threshold
        dt = args.distance_threshold
        ot = args.orientation_threshold
        geometric_similarity(input, st, dt, ot)
    
    elif args.version:
        print(f"Panbiotracks {args.version}")
        sys.exit()

    else:
        print(f"{args.mode} is not a valid option. Please use 'I', "
            "'P', 'N' or 'G'; or use '-h' to get help. For help for a "
            "specific mode, use 'MODE -h'.")