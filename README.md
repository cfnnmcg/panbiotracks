# Panbiotracks

A program to do tracks analysis, Léon Croizat's geometrical approach to biogeography (Croizat, 1958). Currently, it can build individual tracks, internal generalized tracks and generalized nodes, as described in the accompanying article (*in development*).

It has three main functions:

- It builds an individual track from a list of locations in a comma-separated file (CSV) and saves the result to an ESRI shape file (SHP).
- It builds an internal generalized track (IGT) from a set of individual tracks and saves the result to an ESRI shape file (SHP).
- It identifies the intersections between a set of generalized tracks and marks each one as a node, then saves the result to an ESRI shape file (SHP).

## Download and installation

*Panbiotracks* is a self-contained executable that can be run as is, without installing it. To get it, go to the [Releases page](https://github.com/cfnnmcg/panbiotracks/releases) and download the right file according to your operating system. If the file is in compressed format, unpack it before use.

Once downloaded, go to the directory where you saved the executable and open it from a terminal window, like GNOME terminal or Windows PowerShell. Please refer to the [Wiki](https://github.com/cfnnmcg/panbiotracks/wiki) for a more detailed explanation and usage examples.

## Basic usage

### Input files

#### Individual tracks

A comma-separated file (CSV) with three columns/headers: **species**, **lat** and **lon**, in that order. A single file can contain data from multiple species. Latitude and longitude data must be in decimal degrees.

```csv
species,lat,lon
Pinus arizonica,24.983,-105.883
Pinus arizonica,23.423,-104.26
Pinus aristata,36.2942,-105.246
Pinus aristata,38.183333,-106.207222
```

#### Internal generalized tracks

A set of SHP files, each one containing an individual track. There must be at least two of them, separated by a space:

```console
/home/user/shapefile1.shp /home/user/shapefile2.shp
```

The file paths can be relative or absolute.

#### Nodes

A set of SHP files, each one containing an internal generalized track. There must be at least two of them, separated by a space. The file paths can be relative or absolute.

### Individual Tracks

```console
panbiotracks -m I -i [LIST_OF_SPECIES_LOCATIONS.csv] -o [OUTPUT_DIRECTORY]
```

Where **LIST_OF_SPECIES_LOCATIONS.csv** is a single CSV file with a list of species locations represented by a pair of coordinates, like specified in "Input files". **OUTPUT_DIRECTORY** is the name of the directory (folder) where the SHP output files will be saved. This directory can be an existing one or you can write a new name, in which case *Panbiotracks* will create a new directory with that name. If there are data of multiple species in the input CSV file, *Panbiotracks* will generate a SHP file for each of them, named after the data present in the `species` column.

### Internal Generalized Tracks

```console
panbiotracks -m P -i [FILE_1.shp] [FILE_2.shp] [FILE_N.shp] -o [OUTPUT_FILE]
```

Where **FILE_n.shp** are the ESRI shape files that contain the individual tracks that will be used to build the internal generalized track. **OUTPUT_FILE** is the name of the output SHP file, **without** file extension.

### Panbiogeographic Nodes

```console
panbiotracks -m N -i [FILE_1.shp] [FILE_2.shp] [FILE_N.shp] -o [OUTPUT_FILE]
```

Where **FILE_n.shp** are the ESRI shape files that contain the tracks that will be used to build the shape file where the nodes will be saved. **OUTPUT_FILE** is the name of the output SHP file, **without** file extension.

## To do

- Refactor the program to generate generalized tracks and nodes that are more faithful to their formal definition.
- Improve speed and usability.
- Improve the algorithms used.
- Add GeoJSON as an alternative save file format.

## References

- Croizat, L.1958. Panbiogeography. Vols. 1 y 2. Published by the author, Caracas.

## Acknowledgements

This program was made as a fulfillment of the author for obtaining a M.Sc. degree in the Posgrado en Ciencias Biológicas, Universidad Nacional Autónoma de México, Mexico. The author thanks the Consejo Nacional de Humanidades, Ciencias y Tecnologías (CONAHCyT) for the support of this research through a graduate scholarship.

## How to cite

**The accompanying paper is currently in process of revision and waiting to be published.**
