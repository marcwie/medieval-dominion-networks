# Premise

Contains source code for the analysis of medieval co-dominion networks. This is a side-project with [Kerice Doten-Snitker](https://kericedotensnitker.com/) that started during a research visit to the Santa Fe Institute. 

The objective of this project is to investigate the coevolution of political decision-making in medieval Europe. We analyze a network of co-dominion relationships among medieval cities to cluster them into political communities. In this context, co-dominion networks represent instances where two cities are jointly ruled by a single party, such as a bishop governing both simultaneously. We employ these networks to explore the coherence of political behavior within communities, operating on the assumption that policies spread from city to city along the edges of this network.

More information on the project can be found [here](https://kericedotensnitker.com/research/medieval-expulsions/). 

First results will be presented at the [2024 ASREC Conference at Chapman University](https://www.asrec.org/wp-content/uploads/2024/02/ASREC_2024_Preliminary_Program-V02.05..pdf).

# Installation

The package requires [poetry](https://python-poetry.org/). Make sure to have it installed and run `make install` after cloning this repository to install all dependencies.

# Setup

You need input data to make meaningful use of this package. The data will be published in the future. Interested parties can request access. 

Specifically, you need a file that contains information on all nodes and one that contains information on all edges in the network. Both should be `.csv` files. The nodes-file should have the following structure:
```
"","PlaceID","PlaceName","XCOORD","YCOORD","Year","Juden"
"1",1,"Utrecht",3986468.18524327,3232619.45306221,1439,0
"2",1,"Utrecht",3986468.18524327,3232619.45306221,1382,0
"3",1,"Utrecht",3986468.18524327,3232619.45306221,1386,0
"4",1,"Utrecht",3986468.18524327,3232619.45306221,1384,0
...
```
The first column contains a running index. The other columns have the following meaning:
- PlaceID: Unique ID for each node/city.
- PlaceName: The name of the city represented by the node.
- XCOORD: The longitudinal position in [European Grid](https://en.wikipedia.org/wiki/European_grid) coordinates.
- YCOORD: The latitudinal position in [European Grid](https://en.wikipedia.org/wiki/European_grid) coordinates. 
- YEAR: The year for which data has been collected
- Juden: Binary indicator representing whether a Jewish community was present in the city at the given year. 

Similarly, the edges-file should look like this:
```
"","from","to","Year","PartyID"
"1",1,78,1439,"R43"
"2",1,79,1439,"R43"
"3",1,80,1439,"R43"
"4",1,81,1439,"R43"
...
````
Again, the first column contains a running index. The other columns have the following meaning:
- from: The origin of the edge
- to: The destination of the edge
- Year: The year for which data has been collected
- PartyID: Unique Identifier of the party that rules the two cities that are connected with an edge.  

Put both files in `data/01_raw` and set the correct filesnames in `config/main.yaml`.

# Usage

For now, all necessary code is found in `notebooks/1.01-analysis-for-asrec-presentation.ipynb`.

