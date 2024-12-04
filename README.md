# CHEFMODE

# To launch celery
`
    celery -A celery_worker.celery worker --loglevel=info
`
# Run with docker compose

clone the code and run the following command

`docker-compose up -d --build`

access the app on your local

## database
connect to the db container using the following command

docker exec -it chef_mode_db bash

### connet to psql using the following command

`psql -U chefmode`
### create a new user and password for the db

    `CREATE USER chefmode WITH PASSWORD chefmodedb`

### create a new database for the db
    CREATE DATABASE chef_mode_backend OWNER chefmode;


## Run migrations
connect to the web container using the following command

    docker exec -it chef_mode bash

Run the following commands

python manage.py db init

python manage.py db migrate

```python manage.py db upgrade```

https://localhost:5000/admin/

# Run on virtual environment
## Install python virtual environment on Unix os

`python3 -m venv venv`

activate virtual environment

`source venv/bin/activate`

## Install python virtual environment on windows

https://www.liquidweb.com/kb/how-to-setup-a-python-virtual-environment-on-windows-10/

## Install Requirements
    pip install requirements.txt
## install ffmpeg
sudo apt install ffmpeg
To get started, install Postgres on your local computer, if you don’t have it already. Since Heroku uses Postgres, it
will be good for us to develop locally on the same database. If you don’t have Postgres installed, Postgres.app is an
easy way to get up and running for Mac OS X users. Consult the download page for more info.


## Local Migration

#### In order to run the migrations initialize
#### Shell
    $ flask db init

After you run the database initialization you will see a new folder called “migrations” in the project. This holds the setup necessary for Alembic to run migrations against the project. Inside of “migrations” you will see that it has a folder called “versions”, which will contain the migration scripts as they are created.

Let’s create our first migration by running the migrate command.
#### Shell
    $ flask db migrate

Now you’ll notice in your “versions” folder there is a migration file. This file is auto-generated by Alembic based on the model. You could generate (or edit) this file yourself; however, for most cases the auto-generated file will do.

Now we’ll apply the upgrades to the database using the db upgrade command:

    $ flask db upgrade

The database is now ready for us to use in our app:

## start application
just run the manage.py file

        $ flask run
