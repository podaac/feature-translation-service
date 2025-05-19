# Feature Translation Service

The goal of PO.DAAC's Feature Translation Service is to provide hydrologists with a tool that abstracts away unfamiliar NASA dataset terminology and allows them to query NASA information through a more hydrology-specific language.

The Feature Translation Service provides an API for end users to query the [SWOT River Database (SWORD)](https://www.swordexplorer.com/) Feature IDs and Hydrologic Unit Codes (HUCs) plus region identifiers in [USGS's Watershed Boundary Dataset](https://www.usgs.gov/national-hydrography/watershed-boundary-dataset).

It does so through a single, centralized resource in the cloud that first converts these identifiers to geometries removing the need for specific dataset and spatial knowledge.
