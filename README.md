# Panbiotracks

A script to do tracks analysis, Léon Croizat's geometrical approach to biogeography. It has three main functions: one to generate individual tracks, one for generalized tracks and one for panbiogeographic nodes.

`panbiotracks.py` main options are the following:

- `--mode I`: It builds an individual track from a list of locations in a comma-separated file (CSV) and saves the result to an ESRI shape file (SHP).
- `--mode P`: It builds a pseudo-generalized track from a set of individual tracks and saves the result to an ESRI shape file (SHP).
- `--mode N`: It identifies the intersections between a set of generalized tracks and marks each as a node, then saves the result to an ESRI shape file (SHP).

## Basic usage

### Individual Tracks

```console
python panbiotracks.py -m I -i [LIST_OF_LOCATIONS.csv] -o [OUTPUT_FILE]
```

Where **LIST_OF_LOCATIONS.csv** is a single CSV file with a list of locations represented by a pair of coordinates each one and a header. The **latitude** must be in the first column and the **longitude** in the second column. **OUTPUT_FILE** is the name of the output SHP file, **without** file extension.

### Pseudo-Generalized Tracks

```console
python panbiotracks.py -m P -i [FILE_1.shp] [FILE_2.shp] [FILE_N.shp] -o [OUTPUT_FILE]
```

**OUTPUT_FILE** is the name of the output SHP file, **without** file extension.

### Panbiogeographic Nodes

```console
python panbiotracks.py -m N -i [FILE_1.shp] [FILE_2.shp] [FILE_N.shp] -o [OUTPUT_FILE]
```

**OUTPUT_FILE** is the name of the output SHP file, **without** file extension.
