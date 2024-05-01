FROM python:3.12-slim

ARG REPO_DIR

EXPOSE 8000

ENV KASPAD_HOST_1=n.seeder1.kaspad.net:16110
ARG version
ENV VERSION=$version

RUN apt update
RUN apt install uvicorn gunicorn -y

WORKDIR /app
COPY . .

RUN python -m pip install --upgrade pip
RUN pip install poetry
RUN poetry install --no-root --no-interaction

# make pipenv commands still running
RUN ln /usr/local/bin/poetry /usr/local/bin/pipenv

CMD poetry run gunicorn -b 0.0.0.0:8000 -w 4 -k uvicorn.workers.UvicornWorker main:app --timeout 120