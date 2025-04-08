# Overview

URL: `https://fts.podaac.earthdata.nasa.gov/v1`

The Feature Translation Service has several endpoints:

- Rivers: Search for geospatial river data by SWORD reach, node, or river name
- HUC: Search for geospatial river data by USGS HUC identifier
- Region: Search for geospatial river data by USGS region

River reach and node ID numbers are defined in the [SWOT River Database (SWORD)](https://doi.org/10.1029/2021WR030054),
and can be browsed using the [SWORD Explorer Interactive Dashboard](https://www.swordexplorer.com/).

HUC and Region info are defined by the USGS and are defined in [their doucmentation](https://www.usgs.gov/national-hydrography/watershed-boundary-dataset), and can their standard is defined [here](https://pubs.usgs.gov/tm/11/a3/).

PO.DAAC cookbook notebooks:

- [SWORD River Demo](https://podaac.github.io/tutorials/notebooks/SWORD_River_Demo.html)
- [HUC Demo](https://podaac.github.io/tutorials/notebooks/HUC%20Feature%20Translation%20Service%20Examples-updated-20210804.html)
