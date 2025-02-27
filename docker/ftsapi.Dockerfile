FROM public.ecr.aws/lambda/python:3.12

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN ln -s ~/.local/bin/poetry /bin/poetry

# set up project files
COPY poetry.lock pyproject.toml README.md ${LAMBDA_TASK_ROOT}
COPY fts/api/controllers/fts_controller.py ${LAMBDA_TASK_ROOT}/fts/api/controllers/fts_controller.py
RUN touch ${LAMBDA_TASK_ROOT}/fts/api/controllers/__init__.py

# install dependencies
WORKDIR ${LAMBDA_TASK_ROOT}
RUN poetry lock
RUN poetry install --only api --sync \
    && mkdir -p ${LAMBDA_TASK_ROOT}/env \
    && cp -r $(poetry env list --full-path | awk '{print $1}')/lib/python*/site-packages/* ${LAMBDA_TASK_ROOT}/fts/api/controllers

# run the lambda
ENV PYTHONPATH="${PYTHONPATH}:${LAMBDA_TASK_ROOT}/fts/api/controllers"
CMD [ "fts.api.controllers.fts_controller.lambda_handler" ]