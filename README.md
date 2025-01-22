# API

## About

The goal of PO.DAAC's Feature Translation Service is to provide hydrologists with a tool that abstracts away unfamiliar NASA dataset terminology and allows them to query NASA information through a more hydrology-specific language.

The Feature Translation Service provides an API for end users to query NASA’s Common Metadata Repository (CMR) through SWOT Feature IDs and terminology in USGS's [Watershed Boundary Dataset](https://water.usgs.gov/GIS/huc.html) (namely the HUC, or the hydrologic unit code, and the region identifiers). It does so through a single, centralized resource in the cloud that first converts these identifiers to geometries and uses this conversion to then query CMR. Thus, in a way, this service acts as a proxy between CMR and end users, removing the need for specific dataset and spatial knowledge.

This can be seen in the [Examples](examples/) folder in this repository. With the launch of the SWOT satellite in the coming years (and PO.DAAC's ongoing effort to branch into the hydrology sector) it was essential to create a tool that facilitates the ease and efficiency at which the expected influx of hydrologists can query NASA datasets.  

Accompanying documentation can be found by running the following code:

```bash
cd feature-translation-service/docs/_build/html/
open -a "Google Chrome" index.html
```

Or simply navigating to the file under the directory above and double-clicking. Doing either of these will lead to the fully built documentation in Chrome.

## Installation and Deployment

For installation instructions, please see the [terraform deployment directory](terraform/)

# Database

# About

The goal of PO.DAAC's Feature Translation Service is to provide hydrologists with a tool that abstracts away unfamiliar NASA dataset terminology and allows them to query NASA information through a more hydrology-specific language.

The Feature Translation Service provides an API for end users to query NASA’s Common Metadata Repository (CMR) through SWOT Feature IDs and terminology in USGS's [Watershed Boundary Dataset](https://water.usgs.gov/GIS/huc.html) (namely the HUC, or the hydrologic unit code, and the region identifiers). It does so through a single, centralized resource in the cloud that first converts these identifiers to geometries and uses this conversion to then query CMR. Thus, in a way, this service acts as a proxy between CMR and end users, removing the need for specific dataset and spatial knowledge.
