# fargate container
FROM python:3.12-slim

# install OS dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y curl libexpat1 \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VIRTUALENVS_OPTIONS_NO_PIP=true

# drop the unused base pip
RUN python3 -m pip uninstall -y pip

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN ln -s ~/.local/bin/poetry /bin/poetry

# set up project files
WORKDIR /app
COPY poetry.lock pyproject.toml README.md ./
COPY fts/db/sword/setup_sword.py ./fts/db/sword/setup_sword.py

# install dependencies
RUN poetry lock
RUN poetry install

# run command
ENTRYPOINT [ "poetry", "run", "run_sword" ]
