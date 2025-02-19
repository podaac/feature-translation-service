FROM public.ecr.aws/lambda/python:3.12

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN ln -s ~/.local/bin/poetry /bin/poetry

# set up project files
COPY poetry.lock pyproject.toml README.md ${LAMBDA_TASK_ROOT}
COPY fts/api/controllers/fts_controller.py ${LAMBDA_TASK_ROOT}/fts/api/controllers/fts_controller.py

# install dependencies
WORKDIR ${LAMBDA_TASK_ROOT}
RUN poetry lock
RUN poetry install --only api

# run the lambda
CMD ["/var/task/fts/api/controllers/fts_controller.lambda_handler"]