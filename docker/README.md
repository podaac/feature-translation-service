# API Feature Translation Service Docker Image

This directory contains the `Dockerfile` used to build the Docker image capable of running FTS API as a lambda.

It includes a number of helper scripts to be run by the CI/CD pipeline but can also be run locally to build the image.

## Building

Building the FTS API docker image depends on a tar file version of the project. This can be built using `poetry build` or by downloading a previously built version of the project as a tar.

### Building from tar

`build-docker-api.sh` script can be used to build the docker image from the
local tar file. There are two required arguments that must be set:

1. service-name: The name of the service being built (from pyproject.toml)
2. service-version: The version of the service being built (also from pyproject.toml)

The docker tag of the built image will be returned from the script.

Example:

```shell script
./docker/build-docker-api.sh -n podaac-fts -v 1.0.0-alpha.3
```

## Running

The Docker image can be run directly using the `docker run` command.

See [Testing Lambda container images locally](https://docs.aws.amazon.com/lambda/latest/dg/images-test.html) for details.

## Pushing to ECR

The `push-docker-ecr.sh` script can be used to push a docker image to AWS ECR. There are two required arguments:

1. tf-venue: The target venue for uploading (sit, uat, or ops).
2. docker-tag: The docker tage of the image being pushed

The easiest way to use the `push-docker-ecr.sh` script is to first call `build-docker-api.sh` and save the output to the
`docker_tag` environment variable. Then call `push-docker-ecr.sh`.

Example:

```shell script
export docker_tag=$(./docker/build-docker-api.sh -n podaac-fts -v 1.0.0-alpha.3)
./docker/push-docker-ecr.sh -v sit -t $docker_tag
```

# DATABASE Feature Translation Service Docker Image

This directory contains the `Dockerfile` used to build the Docker image capable of running the L2 Subsetter service.

It includes a number of helper scripts to be run by the CI/CD pipeline but can also be run locally to build the image.

## Building

There are two ways to build the Feature Translation Database, from the PO.DAAC Artifactory or from a local poetry build.

### Building from Artifactory

Use the `build-docker-db.sh` script to build the docker image. There are two required arguments that must
be set:

1. service-name: The name of the service being built (from pyproject.toml)
2. service-version: The version of the service being built

This script will then call Docker build which will in turn retrieve the given version of the service from Artifactory
and install it into the Docker image. The docker tag of the built image will be returned from the script.

Example:

```shell script
./docker/build-docker-db.sh -n podaac-fts-database -v 0.2.0
```

### Building from local code

First build the project with Poetry.

```
poetry build
```

That will create a folder `dist/` and a wheel file that is named with the version of the software that was built. 
Similar to building from Artifactory, the `buld-docker-db.sh` script can be used to build the docker image from the
local wheel file. In this case there are still two required arguments that must be set:

1. service-name: The name of the service being built (from pyproject.toml)
2. service-version: The version of the service being built (also from pyproject.toml)

In order to use the local wheel file, call the `build-docker-db.sh` script with the optional argument `--local`. This
will cause the docker image to use the local wheel file instead of downloading the software from Artifactory. 
The docker tag of the built image will be returned from the script.

Example:

```shell script
./docker/build-docker-db.sh -n podaac-fts-database -v 0.3.0a3 --local
```

## Running

The Docker image can be run directly using the `docker run` command.

## Pushing to ECR

The `push-docker-ecr.sh` script can be used to push a docker image to AWS ECR. There are two required arguments:

1. tf-venue: The target venue for uploading (sit, uat, or ops).
2. docker-tag: The docker tage of the image being pushed

The easiest way to use the `push-docker-ecr.sh` script is to first call `build-docker-db.sh` and save the output to the
`docker_tag` environment variable. Then call `push-docker-ecr.sh`.

Example:

```shell script
export docker_tag=$(./docker/build-docker-db.sh -n podaac-fts-database -v 0.1.0)
./docker/push-docker-ecr.sh -v sit -t $docker_tag
```
