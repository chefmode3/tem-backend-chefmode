FROM python:3.10.2-slim-buster


# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install environment dependencies
RUN apt-get update -yqq && apt-get install -yqq --no-install-recommends netcat && apt-get -q clean

# install dependencies
RUN pip install --upgrade pip
CMD ["pip", "install", "greenlet"]
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . .
EXPOSE 5000

# run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
