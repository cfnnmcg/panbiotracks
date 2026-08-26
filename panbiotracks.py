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
import sys

from modules.methods import gen_nodes, generalized_tracks, individual_tracks

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
                    choices=['gpkg', 'gjs', 'shp'],
                    help="Optional. Specifies the output file format. "
                    "Use gpkg for GeoPackage, gjs for GeoJSON, "
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

def main(workmode, i, o, of):
    """
    It checks the selected work mode and calls the appropriate function.
    """
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