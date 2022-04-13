# Tennis Scoreboard

This project contains the REST apis for the Tennis scoreboard app. 

## Project Setup

### Setup Python virtual environment

python3 -m venv .venv

source .venv/bin/activate


### Install requirements

[We use pip-tools for managing dependencies](https://github.com/jazzband/pip-tools)

pip-sync requirements.txt dev-requirements.txt

### Migrate models

python3 manage.py migrate

### Run Tests

python3 manage.py test

### Run development server

python3 manage.py runserver

### API Docs

http://localhost:8000/docs/
