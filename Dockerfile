FROM python:3.10-slim-buster AS builder

# set working directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100
ENV VIRTUAL_ENV="/home/pythonrunner/.venv"
ENV PATH="/home/pythonrunner/.local/bin:${VIRTUAL_ENV}/bin:${PATH}"





# install environment dependencies
RUN apt-get update -yqq && apt-get install -yqq --no-install-recommends netcat && apt-get -q clean

CMD ["ulimit", "-u", "4096"]

COPY . .

RUN pip install --upgrade pip
CMD ["pip", "install", "greenlet"]


RUN pip install -r requirements.txt --no-cache-dir

FROM builder AS dev-container
USER root

# copy app
COPY . /app/

# set work directory
WORKDIR /app

EXPOSE 5001

# run entrypoint.sh
# ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn --bind 0.0.0.0:5000 app:app"]
