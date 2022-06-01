# TSP-Solver
My engineering work

## Introduction
This project is a program to solve Traveling Salesperson Problem, using ant colony algorithm.
Based on it, my engineering work was written. This version has been refreshed, with few code tweaks,
to use existing functions and not write this functionalities myself.

## Usage
Program reads provided database and presents a list of all cities there. User can choose from 2 to all, and after clicking run, a result of ant algorithm will be provided.

## Data
Data in database has been obtained from openstreetmap.org, and parsed to retreive only cities and towns from Silesian Voivodeship in Poland. Then, distances between each city were calculated, using distances in straight line (for simplicity sake). Next all distances greater than 25km were removed, and such data was implemented into sqlite 3 database. This means that any database in that format can be substituted there, and work the same.

When data is loaded into a program missing connections are recreated using Floyd-Warshall algorithm before ant
colony algorithm is run.

## TODO
> Implement "loading bar"
> Implement possibility to have results presented on leaflet like screen
> remove any newly found errors

## errors
program does not detect if a city can be reached at all, so check after Floyd-Warshall algorithm should be performed. This is not a problem for a custom (provided) data.