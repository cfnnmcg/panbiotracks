# Panbiotracks

A program to do tracks analysis, Léon Croizat's geometrical approach to biogeography (Croizat, 1958). Currently, it can build individual tracks, internal generalized tracks and generalized nodes. For more information about these concepts, please read the article mentioned in [How to cite](#how-to-cite).

It has three main functions:

- It builds an individual track from a list of locations in a comma-separated file (CSV) and saves the result to a GeoPackage, GeoJSON or ESRI shape file.
- It builds an internal generalized track (IGT) from a set of individual tracks and saves the result to a GeoPackage, GeoJSON or ESRI shape file.
- It identifies the intersections between a set of generalized tracks and marks each one as a node, then saves the result to a GeoPackage, GeoJSON or ESRI shape file.

## Download and installation

*Panbiotracks* is a self-contained executable that can be run as is, without installation. Go to the [Releases page](https://github.com/cfnnmcg/panbiotracks/releases) and download the appropriate file according to your operating system.

Once downloaded, go to the directory where you saved the executable and open it from a terminal window, like GNOME terminal, macOS Terminal or Windows Terminal or PowerShell. Please refer to the [Wiki](https://github.com/cfnnmcg/panbiotracks/wiki) for a more detailed explanation and usage examples.

## Basic usage

```bash
panbiotracks -m MODE -i INPUT_FILE(S) -o OUTPUT_FILE_OR_DIRECTORY -of OUTPUT_FILE_FORMAT
```

To see the basic help, type:

```bash
panbiotracks -h
```

To check the software version, run:

```bash
panbiotracks -v
```

### Individual Tracks

```bash
panbiotracks -m I -i [SPECIES_LOCATIONS.csv] -o [OUTPUT_DIRECTORY] -of [OUTPUT_FORMAT]
```

Where **SPECIES_LOCATIONS.csv** is a single CSV file with a list of species and their locations with the columns `species,lat,lon`. **OUTPUT_DIRECTORY** is the name of the directory (folder) where the output files will be saved. This can be an existing directory or, if a new directory name is entered, *Panbiotracks* will create it. If there are data of multiple species in the input CSV file, *Panbiotracks* will generate an output file for each of them, using the existing names in the `species` column. **OUTPUT_FORMAT** (optional) is the file format of the output file(s).

### Internal Generalized Tracks

```bash
panbiotracks -m P -i [FILE_1.gpkg] [FILE_2.geojson] [FILE_N.shp] -o [OUTPUT_FILE] -of [OUTPUT_FORMAT]
```

Where **FILE_n.shp** are individual tracks files in the GeoPackage, GeoJSON or ESRI Shapefile format, that will be used to build the internal generalized track. **OUTPUT_FILE** is the path and/or name of the output file, **without** file extension. If the output directory doesn't exists, *Panbiotracks* will create it. **OUTPUT_FORMAT** (optional) is the file format of the output file(s).

### Panbiogeographic Nodes

```bash
panbiotracks -m N -i [FILE_1.gpkg] [FILE_2.geojson] [FILE_N.shp] -o [OUTPUT_FILE] -of [OUTPUT_FORMAT]
```

Where **FILE_n.shp** are generalized track files in the GeoPackage, GeoJSON or ESRI Shapefile format, that will be used to build generalized nodes. **OUTPUT_FILE** is the path and/or name of the output file, **without** file extension. If the output directory doesn't exists, *Panbiotracks* will create it. **OUTPUT_FORMAT** (optional) is the file format of the output file(s).

### Input files

#### For Individual Tracks

A comma-separated file (CSV) with three columns/headers: **species**, **lat** and **lon**, in that order. A single file can contain data from multiple taxa. Latitude and longitude data must be in decimal degrees.

```csv
species,lat,lon
species1,24.983,-105.883
species1,23.423,-104.26
species2,36.2942,-105.246
species2,38.183333,-106.207222
```

#### For Internal Generalized Tracks

A set of files in GeoPackage, GeoJSON or ESRI Shapefile format, each one containing an individual track. There must be at least two of them, separated by a space. File paths can be relative or absolute.

```bash
/home/user/individual_track-1.gpkg /home/user/individual_track-2.geojson /home/user/individual_track-3.shp
```

It's possible to enter a path with wildcards, like

```bash
/home/user/*.gpkg
```

In this case, Panbiotracks will use *all* of the input files within the directory to build the generalized tracks.

#### For Generalized Nodes

A set of files GeoPackage, GeoJSON or ESRI Shapefile format, each one containing a generalized track. There must be at least two of them, separated by a space. File paths can be relative or absolute.

```bash
/home/user/generalized_track-1.gpkg /home/user/generalized_track-2.geojson /home/user/generalized_track-3.shp
```

It's possible to enter a path with wildcards, like

```bash
/home/user/*.gpkg
```

In this case, Panbiotracks will use *all* of the input files within the directory to generate the generalized nodes.

### Output File Format

Optional argument. Specifies the format of the output file(s). Can be `gpkg` for GeoPackage, `gjs` for GeoJSON or `shp` for ESRI Shapefile. If this argument is not provided, *Panbiotracks* will save to the GeoPackage format by default.

```bash
-of {gpkg, gjs, shp}
```

## To do

- Update the program to generate generalized tracks and nodes that are more faithful to their formal definition.
- Improve speed and usability.
- Improve the used algorithms.
- ~~Add GeoJSON as an alternative save file format.~~

## References

- Croizat, L.1958. Panbiogeography. Vols. 1 y 2. Published by the author, Caracas.
- Morrone, J. J. (2015). Track analysis beyond panbiogeography. Journal of Biogeography, 42(3), 413-425. <https://doi.org/10.1111/jbi.12467>

## Acknowledgements

This program was made as a fulfillment of the author for obtaining a M.Sc. degree in the Posgrado en Ciencias Biológicas, Universidad Nacional Autónoma de México, Mexico. The author thanks the Consejo Nacional de Humanidades, Ciencias y Tecnologías (CONAHCyT) for the support of this research through a graduate scholarship.

## How to cite

Castillo-García, C. F., Morrone, J. J., Salgado-Ugarte, I. H., & Espinosa, D. (2025). Panbiotracks: Software for track analysis. *Revista Mexicana de Biodiversidad*, 96, e965429-e965429. <https://doi.org/10.22201/ib.20078706e.2025.96.5429>
