FROM python:3.12-slim

ARG REPO_DIR

EXPOSE 8000

ENV KASPAD_HOST_1=n.seeder1.kaspad.net:16110
ARG version
ENV VERSION=$version

RUN pip install --upgrade pip

RUN pip install \
  pipenv

WORKDIR /app

COPY --chown=api:api . /app

RUN pipenv install --deploy -v

ENTRYPOINT ["/usr/bin/dumb-init", "--"]

CMD pipenv run gunicorn -b 0.0.0.0:8000 -w 1 -k uvicorn.workers.UvicornWorker main:app --timeout 120
