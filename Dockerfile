FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install poetry
RUN python -m poetry config virtualenvs.in-project true
RUN python -m poetry install
RUN source .venv/bin/activate

COPY . .

CMD [ "python", "main.py" ]
