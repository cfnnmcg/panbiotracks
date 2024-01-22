# Panbiotracks

Is a program to do tracks analysis, Léon Croizat's geometrical approach to biogeography. Currently, it generates individual tracks, internal generalized tracks and generalized nodes.

It has three main functions:

- It builds an individual track from a list of locations in a comma-separated file (CSV) and saves the result to an ESRI shape file (SHP).
- It builds a pseudo-generalized track from a set of individual tracks and saves the result to an ESRI shape file (SHP).
- It identifies the intersections between a set of generalized tracks and marks each as a node, then saves the result to an ESRI shape file (SHP).

## Basic usage

### Individual Tracks

```console
panbiotracks -m I -i [LIST_OF_LOCATIONS.csv] -o [OUTPUT_FILE]
```

Where **LIST_OF_LOCATIONS.csv** is a single CSV file with a list of locations represented by a pair of coordinates each one and a header. The **latitude** must be in the first column and the **longitude** in the second column. **OUTPUT_FILE** is the name of the output SHP file, **without** file extension.

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

## Acknowledgements

This program was made as a fulfillment of the author for obtaining a M.Sc. degree in the Posgrado en Ciencias Biológicas, Universidad Nacional Autónoma de México, Mexico. The author thanks the Consejo Nacional de Humanidades, Ciencias y Tecnologías (CONAHCyT) for the support of this research through a graduate scholarship.
