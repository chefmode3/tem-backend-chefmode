#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

gunicorn -b 0.0.0.0:5000 manage:app --certfile=cert.pem --keyfile=key.pem --reload

exec "$@"
