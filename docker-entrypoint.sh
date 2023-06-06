#!/bin/bash

python -m alembic revision --autogenerate
python -m alembic upgrade head

source .venv/bin/activate
python ./main.py
