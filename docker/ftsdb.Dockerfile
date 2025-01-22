# fargate container
FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    && pip3 install --upgrade pip \
    && apt-get clean

RUN adduser --quiet --disabled-password --shell /bin/sh --home /home/dockeruser --uid 1000 dockeruser
ENV HOME /home/dockeruser
ENV PYTHONPATH "${PYTHONPATH}:/home/dockeruser/.local/bin"
ENV PATH="/home/dockeruser/.local/bin:${PATH}"

# Add artifactory as a trusted pip index
RUN mkdir $HOME/.pip
RUN echo "[global]" >> $HOME/.pip/pip.conf && \
    echo "index-url = https://cae-artifactory.jpl.nasa.gov/artifactory/api/pypi/pypi-release-virtual/simple" >> $HOME/.pip/pip.conf && \
    echo "trusted-host = cae-artifactory.jpl.nasa.gov maven.earthdata.nasa.gov pypi.org"  >> $HOME/.pip/pip.conf && \
    echo "extra-index-url = https://maven.earthdata.nasa.gov/repository/python-repo/simple https://pypi.org/simple" >> $HOME/.pip/pip.conf

# The 'SOURCE' argument is what will be used in 'pip install'.
ARG SOURCE

# Set this argument if running the pip install on a local directory, so
# the local dist files are copied into the container.
ARG DIST_PATH

USER dockeruser
WORKDIR "/home/dockeruser"

COPY --chown=dockeruser $DIST_PATH $DIST_PATH
RUN pip3 install --force $SOURCE --user \
    && rm -rf $DIST_PATH

ENTRYPOINT ["run_sword"]