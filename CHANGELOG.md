# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
 
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [1.2.0]
### Added
- Issue #3 - Create GitHub action workflow for CI/CD
- Issue #4 - Host API and database documentation on GitHub pages
### Changed
- Issue #1 - Test FTS refactor and migration to PO.DAAC GitHub organization
### Deprecated
### Removed
### Fixed
### Security

## [1.1.0]
### Added
- PODAAC-3275 - Added new API to search for nodes or reaches by exact river name: /rivers/{name}?reaches=true/false&nodes=true/false
- PODAAC-3470 - Added new API to search for specific node ids or specific reaches by partial river name
- New APIs:
- /rivers/reach/{id}?river_name=red       (query LIKE ('red%'))
- /rivers/node/{id}?river_name=red        (query LIKE ('red%'))
- /rivers/{partial name}?exact=true/false
- Add documentation generation to the build
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [1.0.0]
### Added
- PODAAC-3275 - Added paging to all FTS services.
### Changed
- **BREAKING API CHANGE** Result object has been restructured to return a list of objects instead of the result being an object with many properties.
- Updated terraform deployment to use Terraform 1.0.3  
- PODAAC-3681 - Updated docs for SWORD v11 database schema
### Deprecated
### Removed
### Fixed
### Security

## [0.4.0]
### Added
- PODAAC-3729 - Add indexing to river_name column in reach and node tables
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [0.3.0]
### Added
- PODAAC-3342 - Implemenetation of sphinx autodoc documentation and implemented via Jenkins 
- PODAAC-3681 - Update the FTS database to reflect the latest SWORD v11 schema and import the new v11 data
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [0.2.1]
### Added
### Changed
- PODAAC-3446 Updated value of `geojson` attribute in results of river reaches and nodes to be an object instead of a string
### Deprecated
### Removed
### Fixed
### Security

## [0.2.0]
### Added
- README updates, terraform/bin utlities 
- PODAAC-2978 - Developed a lambda function that is capable of launching a fargate task
- PODAAC-2979 - Added basic python module into a docker container and update the terraform scripts to deploy the fargate task so that the lambda function can launch the fargate task
- PODAAC-2980 - Using if_exists='replace' for pandas RDS load ensures the database is empty before inserting data then SWORD it into the database
- PODAAC-2981 - Created schema and pandas dataframe for creating the database tables so SWORD data can be loaded into the RDS FTS database
- PODAAC-2982 - Created a python module capable of downloading the SWORD data from S3 and extracting / loading the SWORD data from the shapefiles
- PCESA-2989 - Added documentation for FTS SWORD DB
- PODAAC-2984 - Added API Gateway to return river reaches by id (/rivers/reach/{reach})
- PODAAC-2985 - Added API Gateway to return river nodes by id (/rivers/node/{node})
- PODAAC-2986 - Updated API Gateway to return full DB results for reaches and nodes
- PODAAC-2837 - Returns partial results (and http code 206) when hits > 100.
### Changed
- Changed syntax of db creation to drop/create table to avoid duplicates
- PODAAC-2988 - Updated names of components in terraform scripts to be more generic.
### Deprecated 
- Removed scripts/build_lambda and updated documentation. The build lambda script has moved to the `podaac-dev-tools` package. See https://github.jpl.nasa.gov/podaac/dev-tools 
### Removed 
### Fixed 
- PODAAC-2836 - Fixed API errors to return the proper error codes (e.g. 400, 403, 413)
### Security 

## [0.1.0]
### Added
- PCESA-1759 - Apply similar recent changes to staging service to create end to end jenkins pipeline to support the FTS application in end to end consistent automated deployments which are key to being able to release to OPS.
- PCESA-1741 - New polygon_format query param, which can be either flat (default) or geojson.
### Changed 
### Deprecated 
### Removed 
### Fixed 
### Security 