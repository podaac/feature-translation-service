# Overview

URL: `https://fts.podaac.earthdata.nasa.gov/v1`

The Feature Translation Service has several endpoints:

- Rivers: Search for geospatial river data by SWORD reach, node, or river name
- HUC: Search for geospatial river data by USGS HUC identifier
- Region: Search for geospatial river data by USGS region

## SWORD Data

The `rivers` endpoint is used to retrieve data from the SWOT River Database (SWORD). River reach and node ID numbers are defined in the [SWORD](https://doi.org/10.1029/2021WR030054),
and can be browsed using the [SWORD Explorer Interactive Dashboard](https://www.swordexplorer.com/).

PO.DAAC cookbook tutorial: [SWORD River Demo](https://podaac.github.io/tutorials/notebooks/SWORD_River_Demo.html)

## USGS Data

The `huc` and `region` endpoints retrieve data from the USGS Watershed Boundary Dataset. HUC and region info are defined by the USGS in the [Watershed Boundary Dataset](https://www.usgs.gov/national-hydrography/watershed-boundary-dataset).

PO.DAAC cookbook tutorial: [HUC Demo](https://podaac.github.io/tutorials/notebooks/HUC%20Feature%20Translation%20Service%20Examples-updated-20210804.html)
