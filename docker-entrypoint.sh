#!/bin/bash

source .venv/bin/activate
python faqmigrate.py
python ./main.py
