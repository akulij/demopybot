FROM python:3.10

WORKDIR /code
COPY poetry.lock pyproject.toml /code/
COPY alembic alembic.ini /code/

RUN pip install poetry alembic
RUN python -m poetry config virtualenvs.in-project true
RUN python -m poetry install
RUN python -m poetry export -f requirements.txt --output requirements.txt

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["/code/docker-entrypoint.sh"]
# CMD ["python"]
