from __future__ import annotations

import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models.user import User


@click.command('create-user')
@with_appcontext
def create_user_command():
    username = click.prompt('Enter username')
    email = click.prompt('Enter email')
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    click.echo(f"User {username} created.")


@click.command('create_db')
@with_appcontext
def create_db_command():
    db.drop_all()
    db.create_all()
    db.session.commit()


def register(app):
    app.cli.add_command(create_user_command)
    app.cli.add_command(create_db_command)
